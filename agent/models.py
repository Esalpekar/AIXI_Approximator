"""
Core data models for LLM-AIXI project.
Defines the Action and Percept classes that form the agent-environment interface.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Action:
    """
    Represents an action chosen by the agent.
    
    An action consists of selecting a subenvironment and providing input to it.
    This follows the AIXI paradigm where the agent selects actions to interact
    with its environment.
    """
    subenvironment: str  # Name of the subenvironment to interact with
    input_body: str      # Input to send to the subenvironment
    timestamp: datetime = None
    reasoning: str = ""  # Optional: agent's reasoning for this action
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary for serialization."""
        return {
            "subenvironment": self.subenvironment,
            "input_body": self.input_body,
            "timestamp": self.timestamp.isoformat(),
            "reasoning": self.reasoning
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Action":
        """Create action from dictionary."""
        return cls(
            subenvironment=data["subenvironment"],
            input_body=data["input_body"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            reasoning=data.get("reasoning", "")
        )
    
    def __str__(self) -> str:
        """String representation of the action."""
        return f"Action(subenvironment='{self.subenvironment}', input_body='{self.input_body[:50]}...')"


@dataclass
class Percept:
    """
    Represents a percept received by the agent from the environment.
    
    A percept consists of the tool result from the subenvironment and
    the judge's evaluation essay. This follows the AIXI paradigm where
    the agent receives observations and rewards from the environment.
    """
    tool_result: str     # Result from the subenvironment
    judge_essay: str     # Judge's evaluation of the action
    timestamp: datetime = None
    action_reference: Optional[Action] = None  # Reference to the action that caused this percept
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert percept to dictionary for serialization."""
        return {
            "tool_result": self.tool_result,
            "judge_essay": self.judge_essay,
            "timestamp": self.timestamp.isoformat(),
            "action_reference": self.action_reference.to_dict() if self.action_reference else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Percept":
        """Create percept from dictionary."""
        action_ref = None
        if data.get("action_reference"):
            action_ref = Action.from_dict(data["action_reference"])
        
        return cls(
            tool_result=data["tool_result"],
            judge_essay=data["judge_essay"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            action_reference=action_ref
        )
    
    def __str__(self) -> str:
        """String representation of the percept."""
        return f"Percept(tool_result='{self.tool_result[:50]}...', judge_essay='{self.judge_essay[:50]}...')"


@dataclass
class AgentState:
    """
    Represents the current state of the agent.
    
    This includes the full history of actions and percepts, which forms
    the agent's memory and learning foundation.
    """
    cycle_number: int = 0
    history: str = ""
    total_actions: int = 0
    constitution: str = ""
    
    def add_action(self, action: Action) -> None:
        """
        Add an action to the agent's history.
        
        Args:
            action: Action to add to history
        """
        self.total_actions += 1
        action_text = f"\n--- CYCLE {self.cycle_number} ACTION ---\n"
        action_text += f"Timestamp: {action.timestamp.isoformat()}\n"
        action_text += f"Subenvironment: {action.subenvironment}\n"
        action_text += f"Input: {action.input_body}\n"
        if action.reasoning:
            action_text += f"Reasoning: {action.reasoning}\n"
        
        self.history += action_text
    
    def add_percept(self, percept: Percept) -> None:
        """
        Add a percept to the agent's history.
        
        Args:
            percept: Percept to add to history
        """
        percept_text = f"\n--- CYCLE {self.cycle_number} PERCEPT ---\n"
        percept_text += f"Timestamp: {percept.timestamp.isoformat()}\n"
        percept_text += f"Tool Result: {percept.tool_result}\n"
        percept_text += f"\nJudge's Evaluation: {percept.judge_essay}\n"
        percept_text += f"\n{'='*60}\n"
        
        self.history += percept_text
    
    def increment_cycle(self) -> None:
        """Increment the cycle number."""
        self.cycle_number += 1
    
    def get_formatted_history(self) -> str:
        """
        Get the complete formatted history for use in prompts.
        
        Returns:
            Formatted history string
        """
        if not self.history:
            return "No actions taken yet."
        
        return f"AGENT HISTORY (Cycles completed: {self.cycle_number}):\n{self.history}"
    
    def get_last_judge_feedback(self) -> str:
        """
        Extract the most recent judge's feedback from history.
        
        Returns:
            Last judge's evaluation or empty string if none
        """
        if "Judge's Evaluation:" not in self.history:
            return ""
        
        # Find the last occurrence of judge's evaluation
        parts = self.history.split("Judge's Evaluation:")
        if len(parts) > 1:
            # Get the last evaluation and clean it up
            last_eval = parts[-1].split("\n" + "="*60)[0].strip()
            return last_eval
        
        return ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent state to dictionary for serialization."""
        return {
            "cycle_number": self.cycle_number,
            "history": self.history,
            "total_actions": self.total_actions,
            "constitution": self.constitution
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentState":
        """Create agent state from dictionary."""
        return cls(
            cycle_number=data["cycle_number"],
            history=data["history"],
            total_actions=data["total_actions"],
            constitution=data["constitution"]
        )


@dataclass
class ExecutionResult:
    """
    Represents the result of a complete agent execution run.
    
    This contains all the information about a completed run for analysis
    and reporting purposes.
    """
    start_time: datetime
    end_time: datetime
    total_cycles: int
    final_state: AgentState
    success: bool
    error_message: str = ""
    token_usage: Optional[Dict[str, Any]] = None
    
    @property
    def duration(self) -> float:
        """Get the duration of the execution in seconds."""
        return (self.end_time - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert execution result to dictionary for serialization."""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "total_cycles": self.total_cycles,
            "final_state": self.final_state.to_dict(),
            "success": self.success,
            "error_message": self.error_message,
            "token_usage": self.token_usage,
            "duration": self.duration
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionResult":
        """Create execution result from dictionary."""
        return cls(
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            total_cycles=data["total_cycles"],
            final_state=AgentState.from_dict(data["final_state"]),
            success=data["success"],
            error_message=data.get("error_message", ""),
            token_usage=data.get("token_usage")
        )
