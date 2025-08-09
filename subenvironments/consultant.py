"""
Consultant Subenvironment for LLM-AIXI project.
Provides access to a separate LLM for consultation and brainstorming.
"""

import json
from typing import Optional
import vertexai
from vertexai.generative_models import GenerativeModel, HarmCategory, HarmBlockThreshold


class ConsultantSubenvironment:
    """
    LLM consultant for getting second opinions and brainstorming.
    Uses Google Vertex AI Gemini for separate consultation calls.
    """
    
    def __init__(self, project_id: str, location: str = "us-central1", 
                 model_name: str = "gemini-1.5-pro"):
        """
        Initialize the consultant subenvironment.
        
        Args:
            project_id: Google Cloud project ID
            location: Vertex AI location
            model_name: Model to use for consultation
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name

        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)

        # Initialize the model
        self.model = GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.8,  # Slightly higher for creative consultation
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 2048,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
        )
    
    def consult(self, question: str, context: str = "") -> str:
        """
        Consult the LLM with a question.
        
        Args:
            question: The question or problem to consult about
            context: Optional context to provide with the question
            
        Returns:
            LLM response or error message
        """
        try:
            if not question.strip():
                return "ERROR: Question cannot be empty"
            
            # Construct the consultation prompt
            prompt_parts = [
                "You are a helpful AI consultant. You are being asked for advice or a second opinion.",
                "Please provide thoughtful, accurate, and helpful guidance.",
                ""
            ]
            
            if context.strip():
                prompt_parts.extend([
                    "CONTEXT:",
                    context.strip(),
                    ""
                ])
            
            prompt_parts.extend([
                "QUESTION:",
                question.strip(),
                "",
                "Please provide a clear, helpful response:"
            ])
            
            prompt = "\n".join(prompt_parts)
            
            # Make the API call
            response = self.model.generate_content(prompt)
            
            if response.text:
                return f"SUCCESS: Consultation completed.\n\nRESPONSE:\n{response.text}"
            else:
                return "ERROR: No response received from consultant"
                
        except Exception as e:
            return f"ERROR: Consultation failed: {str(e)}"
    
    def brainstorm(self, topic: str, num_ideas: int = 5) -> str:
        """
        Brainstorm ideas on a given topic.
        
        Args:
            topic: Topic to brainstorm about
            num_ideas: Number of ideas to generate
            
        Returns:
            Brainstormed ideas or error message
        """
        try:
            if not topic.strip():
                return "ERROR: Topic cannot be empty"
            
            if num_ideas < 1 or num_ideas > 20:
                return "ERROR: Number of ideas must be between 1 and 20"
            
            prompt = f"""
You are a creative brainstorming assistant. Please generate {num_ideas} creative and practical ideas related to the following topic:

TOPIC: {topic.strip()}

Please provide {num_ideas} distinct ideas, each with a brief explanation. Format your response as a numbered list.
"""
            
            response = self.model.generate_content(prompt)
            
            if response.text:
                return f"SUCCESS: Brainstorming completed for '{topic}'.\n\nIDEAS:\n{response.text}"
            else:
                return "ERROR: No ideas generated"
                
        except Exception as e:
            return f"ERROR: Brainstorming failed: {str(e)}"
    
    def analyze(self, data: str, analysis_type: str = "general") -> str:
        """
        Analyze provided data or information.
        
        Args:
            data: Data or information to analyze
            analysis_type: Type of analysis ("general", "pros_cons", "summary", "critique")
            
        Returns:
            Analysis result or error message
        """
        try:
            if not data.strip():
                return "ERROR: Data to analyze cannot be empty"
            
            analysis_prompts = {
                "general": "Please provide a general analysis of the following information:",
                "pros_cons": "Please analyze the pros and cons of the following:",
                "summary": "Please provide a concise summary of the following:",
                "critique": "Please provide a constructive critique of the following:"
            }
            
            if analysis_type not in analysis_prompts:
                return f"ERROR: Unknown analysis type '{analysis_type}'. Available: general, pros_cons, summary, critique"
            
            prompt = f"""
{analysis_prompts[analysis_type]}

DATA TO ANALYZE:
{data.strip()}

Please provide a thorough and insightful analysis:
"""
            
            response = self.model.generate_content(prompt)
            
            if response.text:
                return f"SUCCESS: {analysis_type.title()} analysis completed.\n\nANALYSIS:\n{response.text}"
            else:
                return "ERROR: No analysis generated"
                
        except Exception as e:
            return f"ERROR: Analysis failed: {str(e)}"


# Main interface function for the orchestrator
def process_consultant_action(input_body: str) -> str:
    """
    Process a consultant action from the agent.
    
    Expected input format (JSON):
    {
        "action": "consult" | "brainstorm" | "analyze",
        "question": "question for consult action",
        "context": "optional context for consult action",
        "topic": "topic for brainstorm action",
        "num_ideas": 5,  // optional for brainstorm
        "data": "data for analyze action",
        "analysis_type": "general"  // optional for analyze
    }
    
    Args:
        input_body: JSON string with consultation details
        
    Returns:
        Consultation result or error message
    """
    try:
        data = json.loads(input_body)
        action = data.get("action")

        # Load configuration and create consultant
        from Config.config import load_vertex_config
        vertex_config = load_vertex_config()
        consultant = ConsultantSubenvironment(
            project_id=vertex_config.project_id,
            location=vertex_config.location,
            model_name=vertex_config.model_name
        )

        if action == "consult":
            question = data.get("question", "")
            context = data.get("context", "")
            return consultant.consult(question, context)
        elif action == "brainstorm":
            topic = data.get("topic", "")
            num_ideas = data.get("num_ideas", 5)
            return consultant.brainstorm(topic, num_ideas)
        elif action == "analyze":
            analyze_data = data.get("data", "")
            analysis_type = data.get("analysis_type", "general")
            return consultant.analyze(analyze_data, analysis_type)
        else:
            return f"ERROR: Unknown action '{action}'. Available: consult, brainstorm, analyze"
        
    except json.JSONDecodeError as e:
        return f"ERROR: Invalid JSON input: {str(e)}"
    except Exception as e:
        return f"ERROR: Consultant operation failed: {str(e)}"


# Documentation for the agent
CONSULTANT_DOCS = """
CONSULTANT SUBENVIRONMENT

This subenvironment provides access to a separate LLM for consultation and brainstorming.
It's useful for getting second opinions without polluting the main reasoning history.

INPUT FORMAT (JSON):
{
    "action": "consult" | "brainstorm" | "analyze",
    
    // For "consult" action:
    "question": "What should I do about X?",
    "context": "optional background information",
    
    // For "brainstorm" action:
    "topic": "topic to brainstorm about",
    "num_ideas": 5,  // optional, 1-20, default 5
    
    // For "analyze" action:
    "data": "information to analyze",
    "analysis_type": "general"  // optional: general, pros_cons, summary, critique
}

ACTIONS:
- consult: Ask for advice or a second opinion on a question
- brainstorm: Generate creative ideas on a topic
- analyze: Analyze data or information with different perspectives

EXAMPLES:
{"action": "consult", "question": "How should I approach this problem?", "context": "I'm working on..."}
{"action": "brainstorm", "topic": "ways to improve code efficiency", "num_ideas": 7}
{"action": "analyze", "data": "Here's my plan...", "analysis_type": "pros_cons"}

NOTES:
- Requires Google Vertex AI configuration
- Uses separate model instance to avoid contaminating main reasoning
- Responses are independent of main agent history
- Useful for creative thinking and problem-solving
"""
