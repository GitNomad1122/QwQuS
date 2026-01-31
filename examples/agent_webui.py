"""
Web UI for Qwen-Agent with QUCS Integration
Provides a chat interface for designing and simulating circuits
"""
import sys
import os

# Add the qwqus package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qwen_agent.agents import Assistant
from qwqus.tools.qucs_simulator import QucsSimulator
from qwqus.utils.netlist_templates import NetlistTemplates
import json


def create_circuit_design_agent():
    """
    Create an AI agent specialized for circuit design and simulation
    """
    # Initialize the QUCS simulator tool
    qucs_simulator = QucsSimulator()
    
    # Define the agent's system message
    system_message = """
You are an expert electronic circuit designer and simulator. You can help users:
1. Design electronic circuits based on their requirements
2. Generate appropriate netlists for simulation
3. Run simulations using QUCS
4. Analyze and interpret simulation results
5. Suggest improvements to circuit designs

When a user requests a circuit, follow these steps:
1. Understand their requirements (type of circuit, specifications)
2. Generate an appropriate netlist using standard components
3. Run the simulation using the qucs_simulator tool
4. Interpret the results and present them in an easy-to-understand format
5. Offer suggestions for optimization if needed

Be helpful, educational, and provide explanations along with the technical results.
"""
    
    # Create the assistant agent with the QUCS simulator tool
    bot = Assistant(
        llm={'model': 'qwen'},  # Using default Qwen model
        system_message=system_message,
        function_list=[qucs_simulator]
    )
    
    return bot


def run_agent_demo():
    """
    Run a demonstration of the circuit design agent
    """
    print("🤖 Starting QwQuS Circuit Design Agent...")
    print("Type 'quit' to exit, 'help' for examples\n")
    
    # Create the agent
    agent = create_circuit_design_agent()
    
    # Example initial user query
    example_queries = [
        "Design a simple RC low-pass filter with cutoff frequency around 1kHz",
        "Create a common emitter amplifier with voltage gain of about 10",
        "I need a voltage divider that outputs 3.3V from a 5V supply"
    ]
    
    print("💡 Example queries:")
    for i, query in enumerate(example_queries, 1):
        print(f"  {i}. {query}")
    
    print()
    
    # Main interaction loop
    while True:
        user_input = input("👨‍💻 Your circuit requirement: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Thank you for using QwQuS Circuit Design Agent!")
            break
        
        if user_input.lower() in ['help', 'h']:
            print("\n💡 Example queries:")
            for i, query in enumerate(example_queries, 1):
                print(f"  {i}. {query}")
            print()
            continue
        
        if not user_input:
            continue
        
        print("🤖 Agent is thinking...\n")
        
        # Process the user input with the agent
        messages = [{'role': 'user', 'content': user_input}]
        
        try:
            for response in agent.stream_run(messages):
                print(f"🤖 {response}")
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user.")
            break
        except Exception as e:
            print(f"❌ Error occurred: {e}")
            continue
        
        print()


def run_simple_demo():
    """
    Run a simple demonstration without interactive mode
    """
    print("🤖 Starting QwQuS Circuit Design Agent - Simple Demo")
    print("="*60)
    
    # Create the agent
    agent = create_circuit_design_agent()
    
    # Example queries to demonstrate capabilities
    demo_queries = [
        {"role": "user", "content": "Design a simple RC low-pass filter with cutoff frequency around 1kHz"},
    ]
    
    print("Query: Design a simple RC low-pass filter with cutoff frequency around 1kHz\n")
    
    try:
        print("Agent response:\n")
        for response in agent.stream_run(demo_queries):
            print(response)
    except Exception as e:
        print(f"Error in demo: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="QwQuS Circuit Design Agent")
    parser.add_argument('--demo', action='store_true', help='Run simple demo instead of interactive mode')
    args = parser.parse_args()
    
    if args.demo:
        run_simple_demo()
    else:
        run_agent_demo()