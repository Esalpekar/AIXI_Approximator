# project_root/subenvironments/query_human.py

class HumanQuerier:
    """
    A tool to pause the agent's execution and ask the human user for direct input.
    This tool is intentionally designed to be disruptive to the agent's autonomous flow,
    reflecting its high cost.
    """

    def query(self, question: str) -> str:
        """
        Poses a question to the human user and waits for their text response.

        Args:
            question: The question to ask the human user.

        Returns:
            The raw string response from the human user.
        """
        # Print a clear, attention-grabbing header to notify the user
        print("\n" + "="*50)
        print("🤖 AGENT IS REQUESTING HUMAN INPUT 🤖")
        print("="*50)
        
        # Present the agent's question clearly
        print(f"\nAgent's Question: {question}\n")
        
        # Prompt for and capture the user's response
        try:
            response = input("Your Response > ")
        except KeyboardInterrupt:
            print("\nUser cancelled input. Returning empty response.")
            response = "User cancelled the query."

        # Print a footer to signify the end of the interaction
        print("\n" + "="*50)
        print("✅ HUMAN INPUT RECEIVED. AGENT IS RESUMING...")
        print("="*50 + "\n")
        
        return response

def create_human_querier():
    """Factory function for the HumanQuerier tool."""
    querier = HumanQuerier()
    return querier.query