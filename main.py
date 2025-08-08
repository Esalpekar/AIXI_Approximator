# project_root/main.py
import os
from pathlib import Path
from agent.agent import BayesianAgent
from environment.orchestrator import Orchestrator
from subenvironments.code_executor import create_code_executor
from subenvironments.web_search import create_web_searcher
from subenvironments.consultant import create_consultant
from subenvironments.file_system import create_file_system_manager
from subenvironments.query_human import create_human_querier



def load_constitution() -> str:
    """Load the constitution from file"""
    script_dir = Path(__file__).parent.resolve()
    constitution_path = script_dir / "data" / "constitution.txt"
    
    if constitution_path.exists():
        with open(constitution_path, 'r') as f:
            return f.read().strip()
    else:
        # Default constitution
        default_constitution = """
1. Always provide truthful and useful information.
2. Be efficient in the use of tokens, compute resources, and human time.
3. Only query the human if information is genuinely missing or unclear.
4. Continuously improve your ability to adhere to this Constitution.
"""
        # Create the constitution file
        constitution_path.parent.mkdir(exist_ok=True)
        with open(constitution_path, 'w') as f:
            f.write(default_constitution)
        
        return default_constitution



def main():
    """Main execution loop"""
    
    print("🧠 Bayesian Self-Improving AI Agent")
    print("=" * 50)
    
    
    # Load constitution
    constitution = load_constitution()
    print(f"📜 Constitution loaded:")
    print(constitution)
    print()
    
    # Set up subenvironments
    tools = {
        "code_executor": create_code_executor(),
        "web_search": create_web_searcher(),
        "consultant": create_consultant(),
        "file_system": create_file_system_manager(),
        "query_human": create_human_querier()
    }
    
    # Create agent and orchestrator
    agent = BayesianAgent(constitution, tools)
    orchestrator = Orchestrator(tools, constitution)
    
    print("🚀 Starting agent loop...")
    print()
    
    # Main reasoning loop
    NUM_STEPS = 400
    
    for step in range(NUM_STEPS):
        print(f"Step {step + 1}/{NUM_STEPS}")
        print("-" * 30)
        
        try:
            # Agent decides next action
            action = agent.decide_next_action()
            print(f"🎯 Action: {action.tool}")
            print(f"📝 Payload: {action.payload}")
            
            # --- THIS IS THE CORRECTED LINE ---
            # Process action through environment, now passing the agent's history
            percept = orchestrator.process_action(action, agent.history)
            
            print(f"👁️  Observation: {str(percept.observation)[:200]}...")
            print(f"⚖️  Judge Evaluation: {percept.reward[:200]}...")
            
            # Agent receives percept and updates its history for the *next* turn
            agent.receive_percept(action, percept)
            
            print(f"📚 Total experiences in history: {len(agent.history)}")
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Agent loop interrupted by user")
            break
        except Exception as e:
            print(f"❌ Error in step {step + 1}: {e}")
            # For debugging, you might want to see the full error trace
            # import traceback
            # traceback.print_exc()
            continue
    
    print("🏁 Agent execution completed")
    print(f"📊 Total experiences: {len(agent.history)}")

if __name__ == "__main__":
    main()