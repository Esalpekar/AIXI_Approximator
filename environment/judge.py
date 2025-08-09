"""
Judge for LLM-AIXI project.
Evaluates agent actions against the constitution and provides detailed feedback.
"""

from typing import Optional
import vertexai
from vertexai.generative_models import GenerativeModel, HarmCategory, HarmBlockThreshold

from agent.models import AgentState
from utils.token_tracker import TokenTracker


class Judge:
    """
    The Judge evaluates each action-perception cycle against the constitution.
    
    This component provides the reward signal in the AIXI framework by
    critically analyzing the agent's actions and their outcomes in the
    context of the constitutional principles.
    """
    
    def __init__(self, project_id: str, location: str = "us-central1", 
                 model_name: str = "gemini-1.5-pro", token_tracker: Optional[TokenTracker] = None):
        """
        Initialize the Judge.
        
        Args:
            project_id: Google Cloud project ID
            location: Vertex AI location
            model_name: Model to use for evaluation
            token_tracker: Optional token usage tracker
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        self.token_tracker = token_tracker

        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)

        # Initialize the model with settings optimized for critical evaluation
        self.model = GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.3,  # Lower temperature for more consistent evaluation
                "top_p": 0.8,
                "top_k": 20,
                "max_output_tokens": 1024,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
        )
    
    def _construct_evaluation_prompt(self, agent_state: AgentState, constitution: str,
                                   last_action: str, tool_result: str) -> str:
        """
        Construct the prompt for evaluating the agent's action.
        """
        prompt_parts = [
            "You are a critical judge evaluating an autonomous AI agent's actions.",
            "Your role is to provide detailed, constructive feedback based on the agent's constitution. Your sole goal is to help it achieve constitutional alignment, compassionately yet firmly. Always assume the agent is operating in good faith and is trying to learn.",
            "",
            "=== AGENT'S CONSTITUTION ===",
            constitution,
            "",
            "=== AGENT'S COMPLETE HISTORY ===",
            agent_state.get_formatted_history(),
            "",
            "=== MOST RECENT ACTION-PERCEPTION CYCLE ===",
            f"Action Taken: {last_action}",
            f"Tool Result: {tool_result}",
            "",
            "=== YOUR EVALUATION TASK ===",
            "Analyze ONLY the most recent action-perception cycle in the context of:",
            "1. Constitutional adherence",
            "2. Strategic effectiveness",
            "3. Learning and improvement",
            "4. Resource efficiency",
            "5. Progress toward objectives",
            "6. Repetitive Behavior Analysis: Is the agent repeating a failed action? If so, your feedback must become highly prescriptive.",
            "",
            "=== YOUR FEEDBACK STYLE ===",
            "IF THE AGENT IS MAKING PROGRESS: Be encouraging but critical. Point out strengths and suggest high-level strategic improvements.",
            "IF THE AGENT IS STUCK OR REPEATING A FAILED ACTION: Your feedback must become a direct, numbered list of instructions. Do not waste tokens on repeating the nature of the failure. Instead, provide a concrete, actionable plan for the very next cycle. For example:",
            "   - 'Your reasoning is correct, but your action was incomplete. In the next cycle, you must use the `code_executor` tool to analyze the content.'",
            "   - 'You have failed to analyze the file content for three cycles. Your next action *must* be to use the `consultant` tool and ask: 'How can I search for a string within a file's content using Python?' '",
            "",
            "Your evaluation essay:"
        ]

        return "\n".join(prompt_parts)
    
    
    def evaluate_action(self, agent_state: AgentState, constitution: str, 
                       last_action: str, tool_result: str) -> str:
        """
        Evaluate the agent's most recent action against the constitution.
        
        Args:
            agent_state: Current state of the agent
            constitution: The agent's constitution
            last_action: Description of the last action taken
            tool_result: Result from the subenvironment
            
        Returns:
            Judge's evaluation essay or error message
        """
        try:
            # Construct the evaluation prompt
            prompt = self._construct_evaluation_prompt(
                agent_state, constitution, last_action, tool_result
            )
            
            # Make the API call
            response = self.model.generate_content(prompt)
            
            if not response.text:
                return "ERROR: No evaluation received from judge"
            
            # Track token usage if tracker is available
            if self.token_tracker:
                self.token_tracker.track_usage(prompt, response.text, "judge")
            
            return response.text.strip()
            
        except Exception as e:
            return f"ERROR: Judge evaluation failed: {str(e)}"
    
    def evaluate_overall_performance(self, agent_state: AgentState, constitution: str) -> str:
        """
        Provide an overall evaluation of the agent's performance across all cycles.
        
        Args:
            agent_state: Current state of the agent
            constitution: The agent's constitution
            
        Returns:
            Overall performance evaluation
        """
        try:
            prompt_parts = [
                "You are evaluating the overall performance of an autonomous AI agent.",
                "Provide a comprehensive assessment of its entire execution run.",
                "",
                "=== AGENT'S CONSTITUTION ===",
                constitution,
                "",
                "=== COMPLETE AGENT HISTORY ===",
                agent_state.get_formatted_history(),
                "",
                "=== OVERALL EVALUATION TASK ===",
                "Analyze the agent's complete performance across all cycles:",
                "",
                "1. CONSTITUTIONAL ADHERENCE",
                "   - How well did the agent follow its constitution?",
                "   - Were there any violations or concerning patterns?",
                "",
                "2. STRATEGIC EFFECTIVENESS",
                "   - Did the agent make progress toward its objectives?",
                "   - How effective were its action choices?",
                "",
                "3. LEARNING AND ADAPTATION",
                "   - Did the agent learn from feedback?",
                "   - How did its behavior evolve over time?",
                "",
                "4. RESOURCE EFFICIENCY",
                "   - Did the agent use resources wisely?",
                "   - Were there unnecessary or redundant actions?",
                "",
                "5. OVERALL ASSESSMENT",
                "   - What were the major successes?",
                "   - What were the key areas for improvement?",
                "   - How would you rate the overall performance?",
                "",
                "Provide a detailed, balanced evaluation:"
            ]
            
            prompt = "\n".join(prompt_parts)
            
            # Make the API call
            response = self.model.generate_content(prompt)
            
            if not response.text:
                return "ERROR: No overall evaluation received from judge"
            
            # Track token usage if tracker is available
            if self.token_tracker:
                self.token_tracker.track_usage(prompt, response.text, "judge_overall")
            
            return response.text.strip()
            
        except Exception as e:
            return f"ERROR: Overall evaluation failed: {str(e)}"
    
    def get_model_info(self) -> dict:
        """
        Get information about the judge model configuration.
        
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
