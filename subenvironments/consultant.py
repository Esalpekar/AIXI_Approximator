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

#    def __init__(self):
#        self.client = OpenAI(
#            base_url="https://openrouter.ai/api/v1",
#            api_key="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"  # Replace with your actual OpenRouter API key
#        )
#        self.deployment = "deepseek/deepseek-prover-v2:free"
    
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
