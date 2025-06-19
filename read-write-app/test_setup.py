#!/usr/bin/env python3
"""
Test script to verify Read-Write App setup
"""

import os
import sys
import asyncio
from pathlib import Path

def test_imports():
    """Test if required packages can be imported"""
    print("Testing imports...")
    
    try:
        from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
        from google.adk.tools import AgentTool
        print("✅ ADK imports successful")
    except ImportError as e:
        print(f"❌ ADK import failed: {e}")
        return False
    
    try:
        import git
        print("✅ GitPython import successful")
    except ImportError as e:
        print(f"❌ GitPython import failed: {e}")
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
    
    # Check git workspace configuration
    git_vars = ["GIT_WORKSPACE_PATH", "GIT_REPO_URL"]
    for var in git_vars:
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
        from file_operations_agent.agent import (
            root_agent, 
            file_reader_agent, 
            file_writer_agent, 
            git_manager_agent,
            file_analysis_workflow,
            file_creation_workflow,
            parallel_file_operations,
            git_management_loop
        )
        
        print("✅ Agent imports successful")
        print(f"   Root agent: {root_agent.name}")
        print(f"   File reader agent: {file_reader_agent.name}")
        print(f"   File writer agent: {file_writer_agent.name}")
        print(f"   Git manager agent: {git_manager_agent.name}")
        print(f"   File analysis workflow: {file_analysis_workflow.name}")
        print(f"   File creation workflow: {file_creation_workflow.name}")
        print(f"   Parallel operations: {parallel_file_operations.name}")
        print(f"   Git management loop: {git_management_loop.name}")
        
        return True
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False

async def test_file_tools():
    """Test file operation tools"""
    print("\nTesting file operation tools...")
    
    try:
        from file_operations_agent.tools import file_tools
        
        print(f"✅ File tools loaded")
        print(f"   Workspace path: {file_tools.workspace_path}")
        print(f"   Git repo initialized: {file_tools.repo is not None}")
        
        # Test git status
        status_result = file_tools.git_status()
        if "error" not in status_result:
            print(f"   Git status: {status_result.get('current_branch', 'N/A')}")
        else:
            print(f"   Git status: {status_result.get('error', 'Unknown error')}")
        
        return True
    except Exception as e:
        print(f"❌ File tools test failed: {e}")
        return False

async def test_coordinator():
    """Test multi-agent coordinator"""
    print("\nTesting multi-agent coordinator...")
    
    try:
        from file_operations_agent.coordinator import coordinator
        
        print(f"✅ Coordinator loaded")
        agents = coordinator.get_all_agents()
        print(f"   Available agents: {len(agents)}")
        
        for name, agent in agents.items():
            print(f"     - {name}: {agent.description[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ Coordinator test failed: {e}")
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
    print("🔍 Testing Read-Write App Setup")
    print("=" * 50)
    
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
    
    # Test file tools
    if not asyncio.run(test_file_tools()):
        print("\n❌ Setup failed: File tools failed")
        return False
    
    # Test coordinator
    if not asyncio.run(test_coordinator()):
        print("\n❌ Setup failed: Coordinator failed")
        return False
    
    # Test A2A configuration
    asyncio.run(test_a2a_config())
    
    print("\n" + "=" * 50)
    print("✅ Setup test completed!")
    print("\nNext steps:")
    print("1. Configure your .env file with API keys and git settings")
    print("2. Run 'cd app && adk web' to start the application")
    print("3. Open http://localhost:8000 in your browser")
    print("4. Select 'enhanced_file_operations_agent' to start")
    print("\nAvailable agents:")
    print("- enhanced_file_operations_agent (main agent)")
    print("- file_analysis_workflow (sequential workflow)")
    print("- file_creation_workflow (sequential workflow)")
    print("- parallel_file_operations (parallel workflow)")
    print("- git_management_loop (loop workflow)")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 