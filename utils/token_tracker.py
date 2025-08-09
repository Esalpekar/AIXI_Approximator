"""
Token usage tracking and cost estimation for LLM-AIXI project.
Monitors API usage for Google Vertex AI calls.
"""

import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class TokenUsage:
    """Represents token usage for a single API call."""
    timestamp: datetime
    call_type: str  # "ideator" or "judge"
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float


@dataclass
class TokenTracker:
    """
    Tracks token usage and estimates costs for LLM API calls.
    
    Pricing is based on Google Vertex AI Gemini pricing (as of 2024):
    - Input tokens: $0.00125 per 1K tokens
    - Output tokens: $0.00375 per 1K tokens
    """
    
    usage_history: List[TokenUsage] = field(default_factory=list)
    input_cost_per_1k: float = 0.000075  # USD per 1K input tokens
    output_cost_per_1k: float = 0.00030  # USD per 1K output tokens
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        This is a rough approximation: ~4 characters per token for English text.
        For production use, you'd want to use the actual tokenizer.
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        return max(1, len(text) // 4)
    
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Calculate estimated cost for token usage.
        
        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        input_cost = (prompt_tokens / 1000) * self.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * self.output_cost_per_1k
        return input_cost + output_cost
    
    def track_usage(self, prompt: str, completion: str, call_type: str = "unknown") -> TokenUsage:
        """
        Track usage for a single API call.
        
        Args:
            prompt: The input prompt sent to the LLM
            completion: The response received from the LLM
            call_type: Type of call ("ideator", "judge", "consultant", etc.)
            
        Returns:
            TokenUsage object with tracked information
        """
        prompt_tokens = self.estimate_tokens(prompt)
        completion_tokens = self.estimate_tokens(completion)
        total_tokens = prompt_tokens + completion_tokens
        estimated_cost = self.calculate_cost(prompt_tokens, completion_tokens)
        
        usage = TokenUsage(
            timestamp=datetime.now(),
            call_type=call_type,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost
        )
        
        self.usage_history.append(usage)
        return usage
    
    def get_total_usage(self) -> Dict[str, float]:
        """
        Get total usage statistics.
        
        Returns:
            Dictionary with total tokens and estimated cost
        """
        if not self.usage_history:
            return {
                "total_prompt_tokens": 0,
                "total_completion_tokens": 0,
                "total_tokens": 0,
                "total_estimated_cost": 0.0,
                "total_calls": 0
            }
        
        total_prompt = sum(usage.prompt_tokens for usage in self.usage_history)
        total_completion = sum(usage.completion_tokens for usage in self.usage_history)
        total_tokens = sum(usage.total_tokens for usage in self.usage_history)
        total_cost = sum(usage.estimated_cost for usage in self.usage_history)
        
        return {
            "total_prompt_tokens": total_prompt,
            "total_completion_tokens": total_completion,
            "total_tokens": total_tokens,
            "total_estimated_cost": total_cost,
            "total_calls": len(self.usage_history)
        }
    
    def get_usage_by_type(self) -> Dict[str, Dict[str, float]]:
        """
        Get usage statistics broken down by call type.
        
        Returns:
            Dictionary with usage stats for each call type
        """
        usage_by_type = {}
        
        for usage in self.usage_history:
            call_type = usage.call_type
            if call_type not in usage_by_type:
                usage_by_type[call_type] = {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "estimated_cost": 0.0,
                    "calls": 0
                }
            
            usage_by_type[call_type]["prompt_tokens"] += usage.prompt_tokens
            usage_by_type[call_type]["completion_tokens"] += usage.completion_tokens
            usage_by_type[call_type]["total_tokens"] += usage.total_tokens
            usage_by_type[call_type]["estimated_cost"] += usage.estimated_cost
            usage_by_type[call_type]["calls"] += 1
        
        return usage_by_type
    
    def print_usage_report(self) -> None:
        """Print a detailed usage report to console."""
        total_stats = self.get_total_usage()
        usage_by_type = self.get_usage_by_type()
        
        print("\n" + "="*60)
        print("LLM-AIXI TOKEN USAGE REPORT")
        print("="*60)
        
        print(f"\nTOTAL USAGE:")
        print(f"  Total API Calls: {total_stats['total_calls']}")
        print(f"  Total Prompt Tokens: {total_stats['total_prompt_tokens']:,}")
        print(f"  Total Completion Tokens: {total_stats['total_completion_tokens']:,}")
        print(f"  Total Tokens: {total_stats['total_tokens']:,}")
        print(f"  Estimated Total Cost: ${total_stats['total_estimated_cost']:.4f}")
        
        if usage_by_type:
            print(f"\nUSAGE BY CALL TYPE:")
            for call_type, stats in usage_by_type.items():
                print(f"  {call_type.upper()}:")
                print(f"    Calls: {stats['calls']}")
                print(f"    Tokens: {stats['total_tokens']:,}")
                print(f"    Cost: ${stats['estimated_cost']:.4f}")
        
        print("\n" + "="*60)
    
    def save_usage_report(self, filepath: str) -> None:
        """
        Save detailed usage report to file.
        
        Args:
            filepath: Path to save the report
        """
        total_stats = self.get_total_usage()
        usage_by_type = self.get_usage_by_type()
        
        with open(filepath, 'w') as f:
            f.write("LLM-AIXI Token Usage Report\n")
            f.write("="*50 + "\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            
            f.write("TOTAL USAGE:\n")
            f.write(f"  Total API Calls: {total_stats['total_calls']}\n")
            f.write(f"  Total Prompt Tokens: {total_stats['total_prompt_tokens']:,}\n")
            f.write(f"  Total Completion Tokens: {total_stats['total_completion_tokens']:,}\n")
            f.write(f"  Total Tokens: {total_stats['total_tokens']:,}\n")
            f.write(f"  Estimated Total Cost: ${total_stats['total_estimated_cost']:.4f}\n\n")
            
            if usage_by_type:
                f.write("USAGE BY CALL TYPE:\n")
                for call_type, stats in usage_by_type.items():
                    f.write(f"  {call_type.upper()}:\n")
                    f.write(f"    Calls: {stats['calls']}\n")
                    f.write(f"    Tokens: {stats['total_tokens']:,}\n")
                    f.write(f"    Cost: ${stats['estimated_cost']:.4f}\n")
            
            f.write("\nDETAILED HISTORY:\n")
            for usage in self.usage_history:
                f.write(f"  {usage.timestamp.isoformat()} | {usage.call_type} | ")
                f.write(f"Tokens: {usage.total_tokens} | Cost: ${usage.estimated_cost:.4f}\n")
