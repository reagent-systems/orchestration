#!/usr/bin/env python3
"""
Task Repository Manager

Utility script for managing the separate task workspace git repository.
Handles initialization, syncing, and task lifecycle operations.
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path
import argparse


class TaskRepoManager:
    def __init__(self, task_repo_path="./workspace"):
        self.task_repo_path = Path(task_repo_path)
        self.current_tasks_dir = self.task_repo_path / "current_tasks"
        self.completed_tasks_dir = self.task_repo_path / "completed_tasks"
        
    def ensure_repo_ready(self):
        """Ensure the task repository is ready for operations."""
        if not self.task_repo_path.exists():
            print(f"❌ Task repository not found at {self.task_repo_path}")
            return False
            
        if not (self.task_repo_path / ".git").exists():
            print(f"❌ No git repository found at {self.task_repo_path}")
            return False
            
        # Pull latest changes
        if self._git_command(["pull"]):
            print("✅ Task repository synced")
        else:
            print("⚠️  Could not sync task repository")
            
        return True
    
    def create_task(self, task_id, title, description, assigned_agents):
        """Create a new task in the repository."""
        if not self.ensure_repo_ready():
            return False
            
        task_dir = self.current_tasks_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        
        # Create task metadata
        task_metadata = {
            "task_id": task_id,
            "title": title,
            "description": description,
            "created_by": "orchestration_system",
            "assigned_agents": assigned_agents,
            "status": "not_started",
            "progress": 0.0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "dependencies": [],
            "blockers": [],
            "next_actions": []
        }
        
        task_file = task_dir / "task.json"
        with open(task_file, 'w') as f:
            json.dump(task_metadata, f, indent=2)
            
        # Create initial progress log
        progress_file = task_dir / "progress.log"
        with open(progress_file, 'w') as f:
            f.write(f"=== Task Created: {datetime.now().isoformat()} ===\n")
            f.write(f"Task: {title}\n")
            f.write(f"Assigned to: {', '.join(assigned_agents)}\n")
            f.write(f"Status: Created\n\n")
            
        # Commit the new task
        self._git_command(["add", str(task_dir)])
        self._git_command([
            "commit", "-m", 
            f"[TASK-CREATED] {task_id}: {title}\n\n- Assigned to: {', '.join(assigned_agents)}\n- Status: not_started"
        ])
        
        print(f"✅ Created task {task_id} in {task_dir}")
        return True
    
    def update_task_progress(self, task_id, progress, status, next_actions=None, agent_name="system"):
        """Update task progress and commit changes."""
        if not self.ensure_repo_ready():
            return False
            
        task_dir = self.current_tasks_dir / task_id
        task_file = task_dir / "task.json"
        
        if not task_file.exists():
            print(f"❌ Task {task_id} not found")
            return False
            
        # Update metadata
        with open(task_file, 'r') as f:
            task_data = json.load(f)
            
        task_data["progress"] = progress
        task_data["status"] = status
        task_data["updated_at"] = datetime.now().isoformat()
        if next_actions:
            task_data["next_actions"] = next_actions
            
        with open(task_file, 'w') as f:
            json.dump(task_data, f, indent=2)
            
        # Update progress log
        progress_file = task_dir / "progress.log"
        with open(progress_file, 'a') as f:
            f.write(f"\n=== Progress Update: {datetime.now().isoformat()} ===\n")
            f.write(f"Agent: {agent_name}\n")
            f.write(f"Progress: {progress:.1%}\n")
            f.write(f"Status: {status}\n")
            if next_actions:
                f.write(f"Next actions: {', '.join(next_actions)}\n")
            f.write("\n")
            
        # Commit the update
        self._git_command(["add", str(task_dir)])
        self._git_command([
            "commit", "-m",
            f"[{agent_name.upper()}] {task_id} progress update\n\n- Progress: {progress:.1%}\n- Status: {status}"
        ])
        
        print(f"✅ Updated task {task_id} progress to {progress:.1%}")
        return True
    
    def complete_task(self, task_id, agent_name="system"):
        """Mark task as completed and move to completed_tasks."""
        if not self.ensure_repo_ready():
            return False
            
        task_dir = self.current_tasks_dir / task_id
        if not task_dir.exists():
            print(f"❌ Task {task_id} not found")
            return False
            
        # Update to completed status
        self.update_task_progress(task_id, 1.0, "completed", agent_name=agent_name)
        
        # Move to completed tasks
        completed_dir = self.completed_tasks_dir / task_id
        completed_dir.parent.mkdir(parents=True, exist_ok=True)
        
        subprocess.run(["mv", str(task_dir), str(completed_dir)])
        
        # Commit the completion
        self._git_command(["add", "."])
        self._git_command([
            "commit", "-m",
            f"[{agent_name.upper()}] {task_id} completed\n\n- Moved to completed_tasks\n- Progress: 100%\n- Status: completed"
        ])
        
        print(f"✅ Completed task {task_id}")
        return True
    
    def list_tasks(self, status_filter=None):
        """List tasks with optional status filter."""
        if not self.ensure_repo_ready():
            return []
            
        tasks = []
        
        # Check current tasks
        if self.current_tasks_dir.exists():
            for task_dir in self.current_tasks_dir.iterdir():
                if task_dir.is_dir():
                    task_file = task_dir / "task.json"
                    if task_file.exists():
                        with open(task_file, 'r') as f:
                            task_data = json.load(f)
                            if not status_filter or task_data.get("status") == status_filter:
                                tasks.append(task_data)
        
        return tasks
    
    def _git_command(self, args):
        """Execute git command in task repository."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.task_repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {e.stderr}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Task Repository Manager")
    parser.add_argument("--repo-path", default="./workspace", help="Path to task repository")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Create task
    create_parser = subparsers.add_parser("create", help="Create new task")
    create_parser.add_argument("task_id", help="Task ID")
    create_parser.add_argument("title", help="Task title")
    create_parser.add_argument("description", help="Task description")
    create_parser.add_argument("--agents", nargs="+", required=True, help="Assigned agents")
    
    # Update progress
    update_parser = subparsers.add_parser("update", help="Update task progress")
    update_parser.add_argument("task_id", help="Task ID")
    update_parser.add_argument("progress", type=float, help="Progress (0.0 to 1.0)")
    update_parser.add_argument("status", help="Task status")
    update_parser.add_argument("--agent", default="system", help="Agent name")
    update_parser.add_argument("--next-actions", nargs="+", help="Next actions")
    
    # Complete task
    complete_parser = subparsers.add_parser("complete", help="Complete task")
    complete_parser.add_argument("task_id", help="Task ID")
    complete_parser.add_argument("--agent", default="system", help="Agent name")
    
    # List tasks
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--status", help="Filter by status")
    
    args = parser.parse_args()
    
    manager = TaskRepoManager(args.repo_path)
    
    if args.command == "create":
        manager.create_task(args.task_id, args.title, args.description, args.agents)
    elif args.command == "update":
        manager.update_task_progress(
            args.task_id, args.progress, args.status, 
            args.next_actions, args.agent
        )
    elif args.command == "complete":
        manager.complete_task(args.task_id, args.agent)
    elif args.command == "list":
        tasks = manager.list_tasks(args.status)
        for task in tasks:
            print(f"{task['task_id']}: {task['title']} ({task['status']}) - {task['progress']:.1%}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 