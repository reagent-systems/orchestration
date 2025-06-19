#!/usr/bin/env python3
"""
Test script to verify ADK and A2A setup
"""

import os
import sys
import asyncio
from pathlib import Path

def test_imports():
    """Test if required packages can be imported"""
    print("Testing imports...")
    
    try:
        from google.adk.agents import Agent
        from google.adk.tools import google_search
        print("✅ ADK imports successful")
    except ImportError as e:
        print(f"❌ ADK import failed: {e}")
        return False
    
    try:
        from a2a_sdk import A2AClient, AgentCard
        print("✅ A2A SDK imports successful")
    except ImportError as e:
        print(f"⚠️  A2A SDK import failed: {e}")
        print("   A2A features will be disabled")
    
    return True

def test_environment():
    """Test environment configuration"""
    print("\nTesting environment configuration...")
    
    # Check if .env file exists
    env_file = Path("app/.env")
    if env_file.exists():
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found. Please copy env.example to .env and configure it.")
    
    # Check required environment variables
    required_vars = ["GOOGLE_API_KEY"]
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"⚠️  {var} is not set")
    
    # Check optional A2A variables
    a2a_vars = ["A2A_HOST", "A2A_PORT", "A2A_AUTH_TOKEN"]
    for var in a2a_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"ℹ️  {var} is not set (optional)")

async def test_agent_creation():
    """Test if agents can be created"""
    print("\nTesting agent creation...")
    
    try:
        # Import the agent module
        sys.path.append("app")
        from google_search_agent.agent import root_agent, basic_search_agent
        
        print("✅ Agent imports successful")
        print(f"   Root agent: {root_agent.name}")
        print(f"   Basic agent: {basic_search_agent.name}")
        
        return True
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False

async def test_a2a_config():
    """Test A2A configuration"""
    print("\nTesting A2A configuration...")
    
    try:
        from a2a_config import a2a_config
        
        print(f"✅ A2A config loaded")
        print(f"   Host: {a2a_config.host}")
        print(f"   Port: {a2a_config.port}")
        print(f"   Enabled: {a2a_config.enabled}")
        
        # Test discovery
        await a2a_config._discover_agents()
        agent_count = a2a_config.get_agent_count()
        print(f"   Discovered agents: {agent_count}")
        
        if agent_count > 0:
            agents = a2a_config.get_all_agents()
            for agent in agents:
                print(f"     - {agent.name}: {', '.join(agent.capabilities)}")
        
        return True
    except Exception as e:
        print(f"❌ A2A config test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 Testing Search App Setup")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\n❌ Setup failed: Required imports not available")
        return False
    
    # Test environment
    test_environment()
    
    # Test agent creation
    if not asyncio.run(test_agent_creation()):
        print("\n❌ Setup failed: Agent creation failed")
        return False
    
    # Test A2A configuration
    asyncio.run(test_a2a_config())
    
    print("\n" + "=" * 40)
    print("✅ Setup test completed!")
    print("\nNext steps:")
    print("1. Configure your .env file with API keys")
    print("2. Run 'cd app && adk web' to start the application")
    print("3. Open http://localhost:8000 in your browser")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 