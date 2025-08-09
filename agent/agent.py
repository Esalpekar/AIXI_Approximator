"""
Ideator Agent for LLM-AIXI project.
Implements the main decision-making component that chooses actions based on history and constitution.
"""

import json
import re
from typing import Optional, Tuple
import vertexai
from vertexai.generative_models import GenerativeModel, HarmCategory, HarmBlockThreshold

from .models import Action, AgentState
from utils.token_tracker import TokenTracker


class Ideator:
    """
    The Ideator is the core decision-making component of the LLM-AIXI agent.
    
    It receives the full history, constitution, and tool documentation, then
    uses an LLM to choose the next action. This replaces the uncomputable
    Solomonoff induction in the original AIXI with practical LLM reasoning.
    """
    
    def __init__(self, project_id: str, location: str = "us-central1", 
                 model_name: str = "gemini-1.5-pro", token_tracker: Optional[TokenTracker] = None):
        """
        Initialize the Ideator.
        
        Args:
            project_id: Google Cloud project ID
            location: Vertex AI location
            model_name: Model to use for decision-making
            token_tracker: Optional token usage tracker
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        self.token_tracker = token_tracker

        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)

        # Initialize the model with settings optimized for reasoning
        self.model = GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.7,  # Balanced creativity and consistency
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 4096,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
        )
    
    def _construct_prompt(self, agent_state: AgentState, constitution: str, tool_docs: str) -> str:
        """
        Construct the comprehensive prompt for action selection.
        
        Args:
            agent_state: Current state of the agent
            constitution: The agent's constitution
            tool_docs: Documentation for available tools
            
        Returns:
            Complete prompt string
        """
        prompt_parts = [
            "You are an autonomous AI agent operating under the LLM-AIXI framework.",
            "You must choose your next action based on your constitution, history, and available tools.",
            "",
            "=== YOUR CONSTITUTION ===",
            constitution,
            "",
            "=== AVAILABLE SUBENVIRONMENTS (TOOLS) ===",
            tool_docs,
            "",
            "=== YOUR HISTORY ===",
            agent_state.get_formatted_history(),
            ""
        ]
        
        # Add judge's feedback if available
        last_feedback = agent_state.get_last_judge_feedback()
        if last_feedback:
            prompt_parts.extend([
                "=== JUDGE'S FEEDBACK ON YOUR LAST ACTION ===",
                f"Your last action was evaluated thusly: {last_feedback}",
                "Use this feedback to improve your next action.",
                ""
            ])
        
        prompt_parts.extend([
            "=== INSTRUCTIONS ===",
            "Based on your constitution, history, and any judge feedback, choose your next action.",
            "",
            "You must respond with EXACTLY this format:",
            "",
            "REASONING:",
            "[Explain your reasoning for this action, connecting it to your constitution and goals]",
            "",
            "ACTION:",
            "subenvironment: [name of subenvironment]",
            "input_body: [JSON input for the subenvironment]",
            "",
            "IMPORTANT:",
            "- Follow your constitution strictly",
            "- Learn from judge feedback",
            "- Choose actions that advance your primary objective",
            "- Ensure input_body is valid JSON for the chosen subenvironment",
            "- Be strategic and avoid redundant actions",
            "",
            "Choose your action now:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_response(self, response_text: str) -> Tuple[Optional[Action], str]:
        """
        Parse the LLM response to extract the action.
        
        Args:
            response_text: Raw response from the LLM
            
        Returns:
            Tuple of (Action object or None, error message)
        """
        try:
            # Extract reasoning
            reasoning_match = re.search(r'REASONING:\s*(.*?)(?=ACTION:|$)', response_text, re.DOTALL)
            reasoning = reasoning_match.group(1).strip() if reasoning_match else ""
            
            # Extract action section
            action_match = re.search(r'ACTION:\s*(.*?)$', response_text, re.DOTALL)
            if not action_match:
                return None, "No ACTION section found in response"
            
            action_text = action_match.group(1).strip()
            
            # Parse subenvironment and input_body
            subenvironment_match = re.search(r'subenvironment:\s*(.+)', action_text)
            input_body_match = re.search(r'input_body:\s*(.*)', action_text, re.DOTALL)
            
            if not subenvironment_match:
                return None, "No subenvironment specified in action"
            
            if not input_body_match:
                return None, "No input_body specified in action"
            
            subenvironment = subenvironment_match.group(1).strip()
            input_body = input_body_match.group(1).strip()
            
            # Validate JSON input_body
            try:
                json.loads(input_body)
            except json.JSONDecodeError as e:
                return None, f"Invalid JSON in input_body: {str(e)}"
            
            # Create action
            action = Action(
                subenvironment=subenvironment,
                input_body=input_body,
                reasoning=reasoning
            )
            
            return action, ""
            
        except Exception as e:
            return None, f"Error parsing response: {str(e)}"
    
    def choose_action(self, agent_state: AgentState, constitution: str, tool_docs: str) -> Tuple[Optional[Action], str]:
        """
        Choose the next action for the agent.
        
        Args:
            agent_state: Current state of the agent
            constitution: The agent's constitution
            tool_docs: Documentation for available tools
            
        Returns:
            Tuple of (Action object or None, error message)
        """
        try:
            # Construct the prompt
            prompt = self._construct_prompt(agent_state, constitution, tool_docs)
            
            # Make the API call
            response = self.model.generate_content(prompt)
            
            if not response.text:
                return None, "No response received from LLM"
            
            # Track token usage if tracker is available
            if self.token_tracker:
                self.token_tracker.track_usage(prompt, response.text, "ideator")
            
            # Parse the response
            action, error = self._parse_response(response.text)
            
            if error:
                return None, f"Failed to parse LLM response: {error}"
            
            return action, ""
            
        except Exception as e:
            return None, f"Error in action selection: {str(e)}"
    
    def get_model_info(self) -> dict:
        """
        Get information about the model configuration.
        
        Returns:
            Dictionary with model information
        """
        return {
            "project_id": self.project_id,
            "location": self.location,
            "model_name": self.model_name,
            "temperature": self.model.generation_config.temperature,
            "max_output_tokens": self.model.generation_config.max_output_tokens
        }
