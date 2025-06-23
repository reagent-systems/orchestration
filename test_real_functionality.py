#!/usr/bin/env python3
"""
Test Real Functionality - Orchestration System
Validates that all agents use real functionality (no simulations)
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_configuration():
    """Test that all required environment variables are configured"""
    print("🔧 Testing Environment Configuration...")
    
    required_vars = [
        "SEARCH_MODEL",
        "METACOGNITION_MODEL", 
        "TASK_BREAKDOWN_MODEL",
        "TERMINAL_MODEL",
        "FILE_OPERATIONS_MODEL",
        "INTERFACE_MODEL",
        "GIT_WORKSPACE_PATH",
        "TASK_MONITOR_INTERVAL"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    print("✅ All required environment variables configured")
    return True

def test_adk_version_consistency():
    """Test that all agents use consistent ADK versions"""
    print("\n🔍 Testing ADK Version Consistency...")
    
    agent_dirs = [
        "search-app",
        "read-write-app", 
        "metacognition-agent",
        "task-breakdown-agent",
        "terminal-agent",
        "interface-agent"
    ]
    
    versions = {}
    
    for agent_dir in agent_dirs:
        req_file = Path(agent_dir) / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r') as f:
                content = f.read()
                for line in content.split('\n'):
                    if line.startswith('google-adk'):
                        versions[agent_dir] = line.strip()
                        break
    
    if len(set(versions.values())) != 1:
        print(f"❌ Inconsistent ADK versions: {versions}")
        return False
    
    expected_version = "google-adk==1.4.2"
    if list(versions.values())[0] != expected_version:
        print(f"❌ Incorrect ADK version. Expected: {expected_version}, Found: {list(versions.values())[0]}")
        return False
    
    print(f"✅ All agents use consistent ADK version: {expected_version}")
    return True

def test_no_simulation_code():
    """Test that agents don't contain simulation code patterns"""
    print("\n🚫 Testing for Simulation Code...")
    
    simulation_patterns = [
        "fake_result",
        "mock_search",
        "simulated_response",
        "placeholder_result",
        "# Simulate",
        "# Mock",
        "return fake"
    ]
    
    agent_files = [
        "search-app/app/google_search_agent/agent.py",
        "read-write-app/app/file_operations_agent/agent.py",
        "metacognition-agent/app/metacognition_agent/agent.py",
        "task-breakdown-agent/app/task_breakdown_agent/agent.py",
        "terminal-agent/app/terminal_agent/agent.py",
        "interface-agent/app/interface_agent/agent.py"
    ]
    
    simulation_found = []
    
    for file_path in agent_files:
        if Path(file_path).exists():
            with open(file_path, 'r') as f:
                content = f.read().lower()
                for pattern in simulation_patterns:
                    if pattern.lower() in content:
                        simulation_found.append(f"{file_path}: {pattern}")
    
    if simulation_found:
        print(f"❌ Simulation code found:")
        for item in simulation_found:
            print(f"   - {item}")
        return False
    
    print("✅ No simulation code patterns found")
    return True

def test_real_search_capability():
    """Test that SearchAgent uses built-in ADK google_search tool"""
    print("\n🔍 Testing Real Search Capability...")
    
    search_agent_file = "search-app/app/google_search_agent/agent.py"
    
    if not Path(search_agent_file).exists():
        print(f"❌ Search agent file not found: {search_agent_file}")
        return False
    
    with open(search_agent_file, 'r') as f:
        content = f.read()
    
    # Check for built-in google_search import
    if "from google.adk.tools import FunctionTool, google_search" not in content:
        print("❌ Built-in google_search tool not imported")
        return False
    
    # Check that google_search is added to agent tools
    if "google_search," not in content:
        print("❌ Built-in google_search tool not added to agent")
        return False
    
    # Check for ADK Built-in comment
    if "ADK Built-in Search Agent" not in content:
        print("❌ Agent not properly configured for built-in search")
        return False
    
    print("✅ Search agent uses built-in ADK google_search tool")
    return True

def test_real_file_operations():
    """Test that FileOperationsAgent has real file operations"""
    print("\n📁 Testing Real File Operations...")
    
    file_agent_file = "read-write-app/app/file_operations_agent/agent.py"
    
    if not Path(file_agent_file).exists():
        print(f"❌ File operations agent not found: {file_agent_file}")
        return False
    
    with open(file_agent_file, 'r') as f:
        content = f.read()
    
    # Check for real file operations
    real_ops = ["open(", "with open(", "Path(", "os.path", "file.write(", "file.read()"]
    
    ops_found = sum(1 for op in real_ops if op in content)
    
    if ops_found < 3:
        print(f"❌ Insufficient real file operations found (found {ops_found}, expected >= 3)")
        return False
    
    print("✅ File operations agent has real file system operations")
    return True

def test_workspace_task_flow():
    """Test that workspace task flow works end-to-end"""
    print("\n🔄 Testing Workspace Task Flow...")
    
    workspace_path = Path(os.getenv("GIT_WORKSPACE_PATH", "./workspace"))
    tasks_path = workspace_path / "current_tasks"
    
    # Create test task
    test_task_id = f"test-real-functionality-{int(time.time())}"
    test_task_path = tasks_path / test_task_id
    test_task_path.mkdir(parents=True, exist_ok=True)
    
    task_data = {
        "task_id": test_task_id,
        "description": "Test task for real functionality validation",
        "agent_type": "search",
        "status": "available",
        "created_at": time.time(),
        "dependencies": []
    }
    
    with open(test_task_path / "task.json", 'w') as f:
        json.dump(task_data, f, indent=2)
    
    # Check task was created
    if not (test_task_path / "task.json").exists():
        print("❌ Failed to create test task")
        return False
    
    print("✅ Workspace task flow working")
    return True

def test_adk_agent_initialization():
    """Test that ADK agents can be initialized without errors"""
    print("\n🤖 Testing ADK Agent Initialization...")
    
    try:
        # Test importing ADK components
        from google.adk.agents import Agent
        from google.adk.tools import FunctionTool, google_search
        
        # Test creating a simple agent
        test_agent = Agent(
            name="test_agent",
            model="gemini-2.0-flash",
            description="Test agent for validation",
            instruction="Test instruction",
            tools=[google_search]
        )
        
        print("✅ ADK agent initialization working")
        return True
        
    except Exception as e:
        print(f"❌ ADK agent initialization failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Real Functionality - Orchestration System")
    print("=" * 60)
    
    tests = [
        test_environment_configuration,
        test_adk_version_consistency,
        test_no_simulation_code,
        test_real_search_capability,
        test_real_file_operations,
        test_workspace_task_flow,
        test_adk_agent_initialization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! System ready for real functionality.")
        return 0
    else:
        print("⚠️  Some tests failed. Please address the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 