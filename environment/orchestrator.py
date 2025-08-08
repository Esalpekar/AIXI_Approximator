# project_root/environment/orchestrator.py
from typing import Dict, Callable, List, Any
from agent.models import Action, Percept
from .judge import Judge

class Orchestrator:
    """Routes actions to subenvironments and coordinates with the judge"""
    
    def __init__(self, subenvironments: Dict[str, Callable], constitution: str):
        """
        Initializes the Orchestrator.
        
        Args:
            subenvironments (Dict[str, Callable]): A dictionary mapping tool names to their callable functions.
            constitution (str): The agent's guiding principles.
        """
        self.subenvironments = subenvironments
        self.judge = Judge()
        self.constitution = constitution
    
    def _analyze_action_profile(self, action: Action) -> str:
        """Generates a qualitative analysis of an action's cost-benefit profile."""
        cost_benefit_profiles = {
            "consultant": "This action is resource-intensive, consuming significant tokens and time. It should be reserved for complex, high-level strategic questions.",
            "web_search": "This action involves network latency. It is most effective when used with precise, targeted queries to find specific facts or documentation.",
            "code_executor": "This action is computationally moderate. Its primary risk is executing flawed code, which can waste a turn. Best used for small, verifiable snippets.",
            "file_system": "This is a low-cost, low-risk action. It is highly efficient for understanding the project state and for persisting completed work.",
            "query_human": "This is the highest-cost action, as it interrupts the user's workflow. It is only permissible when information is genuinely missing and unrecoverable."
        }
        return cost_benefit_profiles.get(action.tool, "This action has an undefined cost-benefit profile.")

    # FIX 1 of 2: The 'history' list is now accepted as a parameter.
    def process_action(self, action: Action, history: List[Dict[str, Any]]) -> Percept:
        """
        Process an action through the appropriate subenvironment and judge, including historical context.
        
        Args:
            action (Action): The action to be executed.
            history (List[Dict[str, Any]]): The list of recent historical turns.
            
        Returns:
            Percept: An object containing the observation, the judge's evaluation (reward), and cost analysis.
        """
        
        # This is the qualitative cost description.
        cost_analysis = self._analyze_action_profile(action)
        
        # Execute the action in the appropriate subenvironment
        if action.tool not in self.subenvironments:
            observation = f"Error: Unknown tool '{action.tool}'"
        else:
            try:
                # Call the tool function (e.g., the searcher's .search method)
                observation = self.subenvironments[action.tool](action.payload)
            except Exception as e:
                observation = f"Error executing tool '{action.tool}': {str(e)}"
        
        # FIX 2 of 2: The 'history' is now passed down to the judge.
        reward_essay = self.judge.evaluate(
            action=action, 
            observation=observation, 
            constitution=self.constitution,
            history=history
        )
        
        # Return the complete percept, including the new cost analysis
        return Percept(observation=observation, reward=reward_essay, cost_analysis=cost_analysis)