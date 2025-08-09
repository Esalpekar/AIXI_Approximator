"""
Main execution loop for LLM-AIXI project.
Runs the iterative reasoning loop for a fixed number of cycles.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(project_root / "Config" / ".env")

from Config.config import validate_config
from agent import Ideator, AgentState, ExecutionResult
from environment import Judge, Orchestrator
from utils import TokenTracker


def load_constitution(constitution_path: str) -> str:
    """
    Load the constitution from file.
    
    Args:
        constitution_path: Path to constitution file
        
    Returns:
        Constitution text
        
    Raises:
        FileNotFoundError: If constitution file doesn't exist
    """
    try:
        with open(constitution_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Constitution file not found: {constitution_path}")


def save_history(history: str, histories_dir: str) -> str:
    """
    Save the complete history to a timestamped file.
    
    Args:
        history: Complete history string
        histories_dir: Directory to save histories
        
    Returns:
        Path to saved file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"aixi_run_{timestamp}.txt"
    filepath = Path(histories_dir) / filename
    
    # Ensure directory exists
    filepath.parent.mkdir(exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"LLM-AIXI Execution History\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n\n")
        f.write(history)
    
    return str(filepath)


def print_cycle_header(cycle: int, max_cycles: int):
    """Print a formatted header for each cycle."""
    print(f"\n{'='*60}")
    print(f"CYCLE {cycle}/{max_cycles}")
    print(f"{'='*60}")


def print_action_summary(action, cycle: int):
    """Print a summary of the chosen action."""
    print(f"\n[CYCLE {cycle}] ACTION CHOSEN:")
    print(f"  Subenvironment: {action.subenvironment}")
    print(f"  Input: {action.input_body[:100]}{'...' if len(action.input_body) > 100 else ''}")
    if action.reasoning:
        print(f"  Reasoning: {action.reasoning[:150]}{'...' if len(action.reasoning) > 150 else ''}")


def print_percept_summary(percept, cycle: int):
    """Print a summary of the received percept."""
    print(f"\n[CYCLE {cycle}] PERCEPT RECEIVED:")
    print(f"  Tool Result: {percept.tool_result[:100]}{'...' if len(percept.tool_result) > 100 else ''}")
    print(f"  Judge Feedback: {percept.judge_essay[:150]}{'...' if len(percept.judge_essay) > 150 else ''}")


def main():
    """Main execution function."""
    print("LLM-AIXI Agent Starting...")
    print("=" * 60)
    
    try:
        # Load configuration
        print("Loading configuration...")
        vertex_config, system_config = validate_config()
        print(f"✓ Configuration loaded (Project: {vertex_config.project_id})")
        
        # Load constitution
        print("Loading constitution...")
        constitution = load_constitution(system_config.constitution_path)
        print(f"✓ Constitution loaded ({len(constitution)} characters)")
        
        # Initialize components
        print("Initializing components...")
        token_tracker = TokenTracker()
        
        ideator = Ideator(
            project_id=vertex_config.project_id,
            location=vertex_config.location,
            model_name=vertex_config.model_name,
            token_tracker=token_tracker
        )
        
        judge = Judge(
            project_id=vertex_config.project_id,
            location=vertex_config.location,
            model_name=vertex_config.model_name,
            token_tracker=token_tracker
        )
        
        orchestrator = Orchestrator(judge)
        print("✓ All components initialized")
        
        # Get tool documentation
        tool_docs = orchestrator.get_subenvironment_docs()
        print(f"✓ Tool documentation loaded ({len(tool_docs)} characters)")
        
        # Initialize agent state
        agent_state = AgentState(constitution=constitution)
        
        # Record start time
        start_time = datetime.now()
        print(f"\n🚀 Starting execution at {start_time.isoformat()}")
        print(f"Maximum cycles: {system_config.max_cycles}")
        
        # Main execution loop
        for cycle in range(1, system_config.max_cycles + 1):
            print_cycle_header(cycle, system_config.max_cycles)
            
            try:
                # Increment cycle in agent state
                agent_state.increment_cycle()
                
                # Agent chooses action
                print("Agent is choosing action...")
                action, error = ideator.choose_action(agent_state, constitution, tool_docs)
                
                if error:
                    print(f"❌ Error in action selection: {error}")
                    break
                
                print_action_summary(action, cycle)
                
                # Add action to history
                agent_state.add_action(action)
                
                # Process action through orchestrator
                print("Processing action...")
                percept = orchestrator.process_action(action, agent_state, constitution)
                
                print_percept_summary(percept, cycle)
                
                # Add percept to history
                agent_state.add_percept(percept)
                
                print(f"✓ Cycle {cycle} completed successfully")
                
            except KeyboardInterrupt:
                print(f"\n⚠️  Execution interrupted by user at cycle {cycle}")
                break
            except Exception as e:
                print(f"❌ Error in cycle {cycle}: {str(e)}")
                break
        
        # Record end time
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n🏁 Execution completed at {end_time.isoformat()}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Cycles completed: {agent_state.cycle_number}")
        
        # Get overall evaluation from judge
        print("\nGetting overall performance evaluation...")
        overall_evaluation = judge.evaluate_overall_performance(agent_state, constitution)
        
        # Print token usage report
        print("\n" + "="*60)
        print("TOKEN USAGE REPORT")
        print("="*60)
        token_tracker.print_usage_report()
        
        # Save complete history
        print("\nSaving execution history...")
        history_content = agent_state.get_formatted_history()
        history_content += f"\n\n{'='*60}\n"
        history_content += "OVERALL PERFORMANCE EVALUATION\n"
        history_content += f"{'='*60}\n"
        history_content += overall_evaluation
        history_content += f"\n\n{'='*60}\n"
        history_content += "EXECUTION SUMMARY\n"
        history_content += f"{'='*60}\n"
        history_content += f"Start Time: {start_time.isoformat()}\n"
        history_content += f"End Time: {end_time.isoformat()}\n"
        history_content += f"Duration: {duration:.2f} seconds\n"
        history_content += f"Cycles Completed: {agent_state.cycle_number}\n"
        history_content += f"Total Actions: {agent_state.total_actions}\n"
        
        # Add token usage to history
        total_usage = token_tracker.get_total_usage()
        history_content += f"\nToken Usage:\n"
        history_content += f"  Total Calls: {total_usage['total_calls']}\n"
        history_content += f"  Total Tokens: {total_usage['total_tokens']:,}\n"
        history_content += f"  Estimated Cost: ${total_usage['total_estimated_cost']:.4f}\n"
        
        history_file = save_history(history_content, system_config.histories_directory)
        print(f"✓ History saved to: {history_file}")
        
        # Save token usage report
        token_report_file = history_file.replace('.txt', '_tokens.txt')
        token_tracker.save_usage_report(token_report_file)
        print(f"✓ Token report saved to: {token_report_file}")
        
        print(f"\n🎉 LLM-AIXI execution completed successfully!")
        print(f"Check the history file for complete details: {history_file}")
        
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
