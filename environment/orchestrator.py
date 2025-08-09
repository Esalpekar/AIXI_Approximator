"""
Orchestrator for LLM-AIXI project.
Routes actions to subenvironments and coordinates judge evaluation.
"""

from typing import Optional, Dict, Any, Callable
from agent.models import Action, Percept, AgentState
from environment.judge import Judge
from subenvironments import SUBENVIRONMENTS


class Orchestrator:
    """
    The Orchestrator manages the interaction between the agent and its environment.
    
    It routes actions to the appropriate subenvironments, collects results,
    and coordinates with the judge to provide complete percepts back to the agent.
    """
    
    def __init__(self, judge: Judge):
        """
        Initialize the Orchestrator.
        
        Args:
            judge: Judge instance for evaluating actions
        """
        self.judge = judge
        self.subenvironments = SUBENVIRONMENTS
    
    def get_available_subenvironments(self) -> Dict[str, str]:
        """
        Get a list of available subenvironments and their descriptions.
        
        Returns:
            Dictionary mapping subenvironment names to descriptions
        """
        return {name: info["description"] for name, info in self.subenvironments.items()}
    
    def process_action(self, action: Action, agent_state: AgentState, constitution: str) -> Percept:
        """
        Process an action by routing it to the appropriate subenvironment and getting judge evaluation.
        
        Args:
            action: Action to process
            agent_state: Current state of the agent
            constitution: Agent's constitution for judge evaluation
            
        Returns:
            Percept containing tool result and judge evaluation
        """
        # Route action to subenvironment
        tool_result = self._route_to_subenvironment(action)
        
        # Format action description for judge
        action_description = self._format_action_for_judge(action)
        
        # Get judge evaluation
        judge_essay = self.judge.evaluate_action(
            agent_state, constitution, action_description, tool_result
        )
        
        # Create and return percept
        percept = Percept(
            tool_result=tool_result,
            judge_essay=judge_essay,
            action_reference=action
        )
        
        return percept
    
    def _route_to_subenvironment(self, action: Action) -> str:
        """
        Route an action to the appropriate subenvironment.
        
        Args:
            action: Action to route
            
        Returns:
            Result from the subenvironment
        """
        subenvironment_name = action.subenvironment
        
        # Check if subenvironment exists
        if subenvironment_name not in self.subenvironments:
            available = ", ".join(self.subenvironments.keys())
            return f"ERROR: Unknown subenvironment '{subenvironment_name}'. Available: {available}"
        
        # Get the subenvironment function
        subenvironment_info = self.subenvironments[subenvironment_name]
        subenvironment_function = subenvironment_info["function"]
        
        try:
            # Call the subenvironment function
            result = subenvironment_function(action.input_body)
            return result
            
        except Exception as e:
            # Handle errors gracefully - they are treated as standard outputs in AIXI
            return f"ERROR: Subenvironment '{subenvironment_name}' failed: {str(e)}"
    
    def _format_action_for_judge(self, action: Action) -> str:
        """
        Format an action for judge evaluation.
        
        Args:
            action: Action to format
            
        Returns:
            Formatted action description
        """
        formatted = [
            f"Subenvironment: {action.subenvironment}",
            f"Input Body: {action.input_body}",
            f"Timestamp: {action.timestamp.isoformat()}"
        ]
        
        if action.reasoning:
            formatted.append(f"Agent's Reasoning: {action.reasoning}")
        
        return "\n".join(formatted)
    
    def validate_action(self, action: Action) -> tuple[bool, str]:
        """
        Validate an action before processing.
        
        Args:
            action: Action to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if subenvironment exists
        if action.subenvironment not in self.subenvironments:
            available = ", ".join(self.subenvironments.keys())
            return False, f"Unknown subenvironment '{action.subenvironment}'. Available: {available}"
        
        # Check if input_body is provided
        if not action.input_body.strip():
            return False, "Action input_body cannot be empty"
        
        # Additional validation could be added here
        # For example, JSON schema validation for specific subenvironments
        
        return True, ""
    
    def get_subenvironment_docs(self) -> str:
        """
        Get documentation for all available subenvironments.
        
        Returns:
            Combined documentation string
        """
        from subenvironments import get_all_docs
        return get_all_docs()
    
    def test_subenvironment(self, subenvironment_name: str, test_input: str) -> str:
        """
        Test a subenvironment with given input (useful for debugging).
        
        Args:
            subenvironment_name: Name of subenvironment to test
            test_input: Test input to send
            
        Returns:
            Test result
        """
        if subenvironment_name not in self.subenvironments:
            available = ", ".join(self.subenvironments.keys())
            return f"ERROR: Unknown subenvironment '{subenvironment_name}'. Available: {available}"
        
        try:
            subenvironment_function = self.subenvironments[subenvironment_name]["function"]
            result = subenvironment_function(test_input)
            return f"TEST SUCCESS: {result}"
        except Exception as e:
            return f"TEST ERROR: {str(e)}"
    
    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the orchestrator.
        
        Returns:
            Dictionary with orchestrator statistics
        """
        return {
            "available_subenvironments": list(self.subenvironments.keys()),
            "subenvironment_count": len(self.subenvironments),
            "judge_model_info": self.judge.get_model_info()
        }
