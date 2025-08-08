# project_root/agent/agent.py
import json
import os
from openai import AzureOpenAI, OpenAI
from typing import Dict, Callable, List
from .models import Agent, Action, Percept

class BayesianAgent(Agent):
    """
    An agent that uses a Large Language Model to decide its next action,
    based on its constitution, goals, and a high-fidelity text history.
    """

    def __init__(self, constitution: str, tools: Dict[str, Callable]):
        super().__init__(constitution, tools)
        self.client = AzureOpenAI(
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_version="2024-06-01",
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT",)
       )
        self.deployment = "Ministral-3B"

    def _format_history(self) -> str:
        """Formats the last few history entries for the prompt."""
        if not self.history:
            return "No history yet. This is the first action."
            
        formatted_entries = []
        # --- THIS IS THE CORRECTED SECTION ---
        # We now iterate through a list of dictionaries, not tuples.
        for turn in self.history[-10:]:
            # Use .get() for safe access, just in case the dict is malformed
            action = turn.get('action')
            percept = turn.get('percept')

            # Add a safety check in case a turn is malformed
            if not action or not percept:
                continue

            # This logic remains the same, it just uses the extracted variables
            entry = (
                f"  - Action: {action.tool} with payload: {json.dumps(action.payload)}\n"
                f"  - Observation: {str(percept.observation)}...\n" # Truncate long observations
                f"  - Judge's Feedback: {percept.reward}...\n" # Truncate long feedback
                f"  - Action's Cost Profile: {percept.cost_analysis}"
            )
            formatted_entries.append(entry)
        return "\n".join(formatted_entries)

    def decide_next_action(self) -> Action:
        """
        Uses the LLM to decide the next action based on the current state.
        """

        system_prompt = """
You are the reasoning core of an AI agent. Your goal is to achieve the objective defined in your constitution by strategically using a set of available tools. Your response MUST be a single, valid JSON object and nothing else.
"""
        user_prompt = f"""
**CONSTITUTION & GOAL:**
{self.constitution}

---

**FILE SYSTEM CONTEXT:**
All `file_system` operations are sandboxed inside a specific working directory. The tool's output will ALWAYS include a `working_directory` key containing the absolute path of this sandbox. You MUST use this path to understand where your files are and to construct correct relative paths for future commands.

---

**AVAILABLE TOOLS & THEIR PAYLOAD STRUCTURES:**
- **file_system**:
    - To write a file: `{{"operation": "write", "path": "your/file/path.html", "content": "..."}}`
    - To read a file: `{{"operation": "read", "path": "your/file/path.html"}}`
    - To check existence: `{{"operation": "exists", "path": "your/file/path.html"}}`
    - To list files: `{{"operation": "list", "path": "your/directory/"}}`
- **code_executor**: Payload is a string of any code.
- **web_search**: Payload is a string with a search query.
- **consultant**: Payload is a string with your question.
- **query_human**: Payload is a string with a question for the user.

---

**RECENT HISTORY (Uncompressed, High-Fidelity):**
{self._format_history()}

---

**TASK:**
Based on the constitution, your goal, the tools' payload structures, and your recent history, determine the best next action. Return your decision as a JSON object: {{"thought": "A brief thought process on why you chose this action.", "action": {{"tool": "tool_name", "payload": {{...}} or "string"}}}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=10000,
                temperature=0.4,
                response_format={"type": "json_object"}
            )

            decision_json = json.loads(response.choices[0].message.content)
            action_data = decision_json.get("action", {})
            tool = action_data.get("tool")
            payload = action_data.get("payload")

            if tool not in self.tools:
                print(f"WARNING: LLM chose an invalid tool '{tool}'. Defaulting to consultant.")
                return Action("consultant", f"The last chosen tool ('{tool}') was invalid. What is a better next step considering the history?")

            return Action(tool=tool, payload=payload)

        except Exception as e:
            print(f"CRITICAL ERROR: Error during LLM decision making: {e}. Defaulting to a safe action.")
            # import traceback
            # traceback.print_exc()
            return Action("consultant", "I encountered a critical error in my decision-making process and could not parse the response. What should I do next?")