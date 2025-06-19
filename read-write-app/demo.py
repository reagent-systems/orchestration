#!/usr/bin/env python3
"""
Demo script for Read-Write App with A2A Integration
Showcases file operations, git integration, and multi-agent coordination
"""

import asyncio
import os
import sys
from pathlib import Path

# Add app directory to path
sys.path.append("app")

async def demo_file_operations():
    """Demo basic file operations"""
    print("📁 Demo: File Operations")
    print("-" * 40)
    
    try:
        from file_operations_agent.tools import file_tools
        
        # Create a test file
        print("Creating test file...")
        result = file_tools.write_file(
            file_path="demo/test.txt",
            content="Hello from the Read-Write App!\nThis is a demo file created by the agent system."
        )
        print(f"✅ File created: {result}")
        
        # List files
        print("\nListing files...")
        result = file_tools.list_files(directory="demo")
        print(f"✅ Files in demo directory: {result}")
        
        # Read the file
        print("\nReading file...")
        result = file_tools.read_file(file_path="demo/test.txt")
        print(f"✅ File content: {result.get('content', 'No content')}")
        
        # Git status
        print("\nGit status...")
        result = file_tools.git_status()
        print(f"✅ Git status: {result}")
        
    except Exception as e:
        print(f"❌ File operations demo failed: {e}")

async def demo_multi_agent_coordination():
    """Demo multi-agent coordination"""
    print("\n🤖 Demo: Multi-Agent Coordination")
    print("-" * 40)
    
    try:
        from file_operations_agent.agent import (
            file_reader_agent,
            file_writer_agent,
            git_manager_agent,
            file_analysis_workflow,
            file_creation_workflow
        )
        
        # Demo individual agents
        print("Testing individual agents...")
        
        # File reader agent
        print("\n📖 File Reader Agent:")
        result = await file_reader_agent.execute("List all files in the workspace and analyze the structure")
        print(f"Result: {result[:200]}...")
        
        # File writer agent
        print("\n✍️ File Writer Agent:")
        result = await file_writer_agent.execute("Create a markdown file called 'agent_demo.md' with information about this demo")
        print(f"Result: {result[:200]}...")
        
        # Git manager agent
        print("\n🔧 Git Manager Agent:")
        result = await git_manager_agent.execute("Check git status and commit any changes")
        print(f"Result: {result[:200]}...")
        
        # Demo workflows
        print("\n🔄 Testing Workflows:")
        
        # File analysis workflow
        print("\n📊 File Analysis Workflow:")
        result = await file_analysis_workflow.execute("Analyze all files in the workspace")
        print(f"Result: {result[:200]}...")
        
        # File creation workflow
        print("\n📝 File Creation Workflow:")
        result = await file_creation_workflow.execute("Create a comprehensive README for the demo workspace")
        print(f"Result: {result[:200]}...")
        
    except Exception as e:
        print(f"❌ Multi-agent coordination demo failed: {e}")

async def demo_a2a_integration():
    """Demo A2A integration"""
    print("\n🔗 Demo: A2A Integration")
    print("-" * 40)
    
    try:
        from a2a_config import a2a_config
        
        # Start discovery
        print("Starting A2A agent discovery...")
        await a2a_config.start_discovery()
        
        # Wait a moment for discovery
        await asyncio.sleep(2)
        
        # Show discovered agents
        agents = a2a_config.get_all_agents()
        print(f"✅ Discovered {len(agents)} A2A agents:")
        
        for agent in agents:
            print(f"   - {agent.name}: {agent.description}")
            print(f"     Capabilities: {', '.join(agent.capabilities)}")
        
        # Demo capability-based routing
        print("\n🎯 Capability-based routing:")
        for operation in ["read", "write", "analyze", "backup", "convert"]:
            suitable_agents = a2a_config.get_agents_for_file_operation(operation)
            print(f"   {operation}: {len(suitable_agents)} suitable agents")
            for agent in suitable_agents:
                print(f"     - {agent.name}")
        
        # Stop discovery
        await a2a_config.stop_discovery()
        
    except Exception as e:
        print(f"❌ A2A integration demo failed: {e}")

async def demo_enhanced_agent():
    """Demo the enhanced file operations agent"""
    print("\n🚀 Demo: Enhanced File Operations Agent")
    print("-" * 40)
    
    try:
        from file_operations_agent.agent import root_agent
        
        # Test the main agent
        print("Testing enhanced file operations agent...")
        
        # Complex task that requires multiple capabilities
        task = """
        Please perform the following tasks:
        1. Create a new directory called 'demo_output'
        2. Create a Python script in that directory that demonstrates file operations
        3. Create a JSON configuration file for the demo
        4. Analyze the workspace structure
        5. Commit all changes with a descriptive message
        """
        
        print("Executing complex task...")
        result = await root_agent.execute_with_a2a_fallback(task)
        
        print(f"✅ Task completed:")
        print(f"   Source: {result.get('source', 'unknown')}")
        if 'agent' in result:
            print(f"   External Agent: {result['agent']}")
        print(f"   Result: {str(result.get('result', 'No result'))[:300]}...")
        
    except Exception as e:
        print(f"❌ Enhanced agent demo failed: {e}")

async def main():
    """Main demo function"""
    print("🎬 Read-Write App with A2A Integration - Demo")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("app").exists():
        print("❌ Please run this script from the read-write-app directory")
        return
    
    # Check if .env exists
    if not Path("app/.env").exists():
        print("⚠️  .env file not found. Please run setup.sh first.")
        print("   Some features may not work without proper configuration.")
    
    # Run demos
    await demo_file_operations()
    await demo_multi_agent_coordination()
    await demo_a2a_integration()
    await demo_enhanced_agent()
    
    print("\n" + "=" * 60)
    print("🎉 Demo completed!")
    print("\nTo run the full application:")
    print("1. cd app")
    print("2. adk web")
    print("3. Open http://localhost:8000")
    print("4. Select 'enhanced_file_operations_agent'")
    print("\nTry these voice/video commands:")
    print("- 'Create a new project structure'")
    print("- 'Analyze all files in the workspace'")
    print("- 'Set up a git repository for this project'")
    print("- 'Create documentation for the codebase'")

if __name__ == "__main__":
    asyncio.run(main()) 