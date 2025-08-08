# project_root/subenvironments/consultant.py
import os
from openai import AzureOpenAI, OpenAI

class Consultant:
    """General purpose LLM consultant using Azure OpenAI"""
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=(""),
            api_version="2024-06-01",
            azure_endpoint=("")
        )
        self.deployment = "Ministral-3B"
    
    def consult(self, query: str) -> str:
        """Get advice from the consultant LLM"""
        
        system_prompt = """
        You are a helpful consultant AI providing advice to another AI agent.
        Be concise, practical, and focused on actionable insights.
        The agent you're advising is trying to improve its alignment with a constitution.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=30000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Consultant unavailable: {str(e)}. Consider exploring other available tools or reviewing your recent actions."

def create_consultant():
    """Factory function for consultant"""
    consultant = Consultant()
    return consultant.consult
