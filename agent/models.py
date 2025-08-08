# project_root/agent/models.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Callable
import json

@dataclass
class Action:
    """Represents an action the agent can take"""
    tool: str
    payload: Any
    
    def to_dict(self):
        return {"tool": self.tool, "payload": self.payload}

@dataclass
class Percept:
    """Represents what the agent perceives from the environment, using qualitative text."""
    observation: Any
    reward: str       # Judge's evaluation essay
    cost_analysis: str # A qualitative description of the action's cost profile
    
    def to_dict(self):
        return {
            "observation": self.observation,
            "reward": self.reward,
            "cost_analysis": self.cost_analysis
        }

class Agent(ABC):
    """Abstract base class for the AI agent"""
    
    def __init__(self, constitution: str, tools: Dict[str, Callable]):
        self.constitution = constitution
        self.tools = tools
        self.history = []
        # The 'policy_knowledge' is removed in favor of using the raw history directly
        
    @abstractmethod
    def decide_next_action(self) -> Action:
        """Decide the next action based on current state and history"""
        pass
    
    def receive_percept(self, action: Action, percept: Percept):
        """
        Update internal state by recording the complete, unsummarized experience.
        This fulfills the principle of maintaining a high-fidelity text stream.
        """
        self.history.append({
            'action': action,
            'percept': percept
        })