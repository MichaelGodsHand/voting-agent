#!/usr/bin/env python3
"""
Startup script for the Voting Agent

This script provides an easy way to start the Voting Agent with proper
environment setup and error handling.
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Check if required environment variables are set."""
    print("🔍 Checking environment variables...")
    
    # Load environment variables
    load_dotenv()
    
    required_vars = ["ASI_ONE_API_KEY", "AGENTVERSE_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\n📝 Please create a .env file with the following variables:")
        print("ASI_ONE_API_KEY=your_asi_one_api_key_here")
        print("AGENTVERSE_API_KEY=your_agentverse_api_key_here")
        print("\n💡 You can copy env.example to .env and fill in your API keys:")
        print("cp env.example .env")
        return False
    
    print("✅ All required environment variables are set")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "openai",
        "hyperon", 
        "uagents",
        "uagents_core",
        "python-dotenv",
        "requests"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("\n📦 Install missing packages with:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ All required dependencies are installed")
    return True

def start_agent():
    """Start the Voting Agent."""
    print("🚀 Starting Voting Agent...")
    print("=" * 50)
    
    try:
        # Import and run the agent
        from agent import agent
        agent.run()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Voting Agent...")
        print("✅ Agent stopped.")
    except Exception as e:
        print(f"❌ Error starting agent: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure all dependencies are installed")
        print("2. Check that environment variables are set correctly")
        print("3. Ensure port 8081 is not in use")
        print("4. Verify the knowledge graph URL is accessible")

def main():
    """Main function to start the Voting Agent."""
    print("🗳️ Voting Agent Startup Script")
    print("=" * 40)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("\n✅ All checks passed!")
    print("\n🌐 Agent will be available at:")
    print("   - REST API: http://localhost:8081")
    print("   - Chat Protocol: Available for A2A communication")
    print("\n📡 Available endpoints:")
    print("   - POST /voting/question")
    print("   - POST /voting/questions") 
    print("   - POST /brand/negative-data")
    print("\n🧪 Test the agent with:")
    print("   python test_voting_endpoints.py")
    print("   python example_usage.py")
    
    print("\n" + "=" * 50)
    
    # Start the agent
    start_agent()

if __name__ == "__main__":
    main()
