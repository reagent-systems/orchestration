#!/usr/bin/env python3
"""
Simple Test Task Creator
Creates tasks for testing agent orchestration
"""

import json
import time
import sys
from pathlib import Path

def create_task(description: str, agent_type: str = "auto"):
    """Create a test task in the workspace"""
    
    # Ensure workspace exists
    workspace = Path("./workspace")
    tasks_dir = workspace / "current_tasks"
    workspace.mkdir(exist_ok=True)
    tasks_dir.mkdir(exist_ok=True)
    
    # Create task
    task_id = f"test-task-{int(time.time())}-{description[:20].replace(' ', '-').lower()}"
    task_path = tasks_dir / task_id
    task_path.mkdir(exist_ok=True)
    
    task_data = {
        "task_id": task_id,
        "description": description,
        "agent_type": agent_type,
        "status": "available",
        "priority": 3,
        "created_at": time.time(),
        "created_by": "test_script",
        "dependencies": []
    }
    
    # Save task
    with open(task_path / "task.json", 'w') as f:
        json.dump(task_data, f, indent=2)
    
    print(f"✅ Created task: {task_id}")
    print(f"📝 Description: {description}")
    print(f"🤖 Agent type: {agent_type}")
    print(f"📁 Location: {task_path}")
    
    return task_id

def main():
    print("🧪 Test Task Creator")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        # Command line usage
        description = " ".join(sys.argv[1:])
        create_task(description)
    else:
        # Interactive mode
        print("Enter task description (or press Enter for default test):")
        description = input("> ").strip()
        
        if not description:
            description = "Analyze codebase for syntax flaws and compare with fixes from Stack Overflow"
        
        print("\nAgent type (auto/search/terminal/file_operations/planning) [auto]:")
        agent_type = input("> ").strip() or "auto"
        
        create_task(description, agent_type)
    
    print("\n🎯 Now watch the agents in your terminals!")
    print("📁 Open workspace/current_tasks/ in file explorer to see the magic happen")

if __name__ == "__main__":
    main() 