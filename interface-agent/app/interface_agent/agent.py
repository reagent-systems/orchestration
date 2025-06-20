"""
Interface Agent - Human Gateway to Orchestration System
Provides CLI interface for task assignment and system monitoring
"""

import os
import sys
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import subprocess

# Add the scripts directory to the path so we can import task_repo_manager
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "scripts"))
from task_repo_manager import TaskRepoManager

class InterfaceAgent:
    """Human-friendly CLI interface for the orchestration system"""
    
    def __init__(self):
        self.workspace_path = os.getenv("TASK_WORKSPACE_PATH", "./workspace")
        self.task_manager = TaskRepoManager(self.workspace_path)
        self.running = True
        
        # Display configuration
        self.refresh_interval = 2  # seconds for live updates
        
        print("🤖 Interface Agent Initializing...")
        print(f"📁 Workspace: {self.workspace_path}")
        
    def display_banner(self):
        """Display the system banner"""
        print("\n" + "="*60)
        print("🎯 ORCHESTRATION SYSTEM INTERFACE")
        print("="*60)
        print("Human Gateway to Decentralized Multi-Agent System")
        print("Workspace:", self.workspace_path)
        print("Time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("="*60)
    
    def display_main_menu(self):
        """Display the main CLI menu"""
        print("\n📋 MAIN MENU")
        print("-" * 20)
        print("1. 📝 Create New Task")
        print("2. 👀 View Active Tasks")
        print("3. 📊 View Task Progress")
        print("4. 🤖 View Agent Status")
        print("5. 💾 View Completed Tasks")
        print("6. 🔄 Live Progress Monitor")
        print("7. 🧠 System Health")
        print("8. 🚪 Exit")
        print("-" * 20)
    
    def create_task_interactive(self):
        """Interactive task creation wizard"""
        print("\n✨ CREATE NEW TASK")
        print("=" * 30)
        
        try:
            # Get task details from user
            title = input("📝 Task Title: ").strip()
            if not title:
                print("❌ Task title cannot be empty!")
                return
            
            description = input("📄 Description: ").strip()
            if not description:
                description = title
            
            print("\n🎯 Priority Level:")
            print("1. 🔴 High")
            print("2. 🟡 Medium") 
            print("3. 🟢 Low")
            priority_choice = input("Priority (1-3): ").strip()
            priority_map = {"1": "high", "2": "medium", "3": "low"}
            priority = priority_map.get(priority_choice, "medium")
            
            print("\n⚡ Complexity Level:")
            print("1. 🟢 Low (Simple task)")
            print("2. 🟡 Medium (Moderate complexity)")
            print("3. 🔴 High (Complex task)")
            complexity_choice = input("Complexity (1-3): ").strip()
            complexity_map = {"1": "low", "2": "medium", "3": "high"}
            complexity = complexity_map.get(complexity_choice, "medium")
            
            print("\n🤖 Suggested Agents:")
            print("Available: search_agent, read_write_agent, metacognition_agent")
            agents_input = input("Agents (comma-separated, or press Enter for auto): ").strip()
            
            if agents_input:
                agents = [agent.strip() for agent in agents_input.split(",")]
            else:
                # Auto-assign based on task type
                agents = self.suggest_agents(title, description)
                print(f"🎯 Auto-assigned agents: {', '.join(agents)}")
            
            # Generate task ID
            date_str = datetime.now().strftime("%Y-%m-%d")
            task_id = f"task-{date_str}-{title.lower().replace(' ', '-')[:20]}"
            
            # Create the task
            print(f"\n🚀 Creating task: {task_id}")
            success = self.task_manager.create_task(
                task_id=task_id,
                title=title,
                description=description,
                assigned_agents=agents
            )
            
            if success:
                # Add metadata
                self.add_task_metadata(task_id, priority, complexity)
                
                print("✅ Task created successfully!")
                print(f"📋 Task ID: {task_id}")
                print(f"🎯 Priority: {priority}")
                print(f"⚡ Complexity: {complexity}")
                print(f"🤖 Assigned Agents: {', '.join(agents)}")
                print("\n🔔 Agents will be notified and begin processing...")
                
                # Show immediate task status
                self.show_task_details(task_id)
            else:
                print("❌ Failed to create task!")
                
        except KeyboardInterrupt:
            print("\n❌ Task creation cancelled")
        except Exception as e:
            print(f"❌ Error creating task: {e}")
    
    def suggest_agents(self, title: str, description: str) -> List[str]:
        """Auto-suggest agents based on task content"""
        agents = ["metacognition_agent"]  # Always include metacognition for planning
        
        text = (title + " " + description).lower()
        
        # Search-related keywords
        if any(keyword in text for keyword in ["search", "research", "find", "information", "web", "google"]):
            agents.append("search_agent")
        
        # File-related keywords  
        if any(keyword in text for keyword in ["file", "write", "read", "document", "git", "workspace"]):
            agents.append("read_write_agent")
        
        return agents
    
    def add_task_metadata(self, task_id: str, priority: str, complexity: str):
        """Add additional metadata to task"""
        try:
            task_dir = Path(self.workspace_path) / "current_tasks" / task_id
            metadata_file = task_dir / "metadata.json"
            
            metadata = {
                "priority": priority,
                "complexity": complexity,
                "created_via": "interface_agent",
                "created_at": datetime.now().isoformat(),
                "human_assigned": True
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Warning: Could not add metadata: {e}")
    
    def view_active_tasks(self):
        """Display all active tasks"""
        print("\n📋 ACTIVE TASKS")
        print("=" * 40)
        
        try:
            tasks = self.task_manager.list_tasks()
            active_tasks = [t for t in tasks if t.get("status") not in ["completed", "cancelled"]]
            
            if not active_tasks:
                print("📭 No active tasks found")
                return
            
            for i, task in enumerate(active_tasks, 1):
                self.display_task_summary(i, task)
                
        except Exception as e:
            print(f"❌ Error retrieving tasks: {e}")
    
    def display_task_summary(self, index: int, task: Dict[str, Any]):
        """Display a summary of a single task"""
        task_id = task.get("task_id", "unknown")
        title = task.get("title", "No title")
        status = task.get("status", "unknown")
        progress = task.get("progress", 0)
        agents = task.get("assigned_agents", [])
        
        # Status emoji
        status_emoji = {
            "not_started": "⏳",
            "in_progress": "🔄", 
            "blocked": "🚫",
            "completed": "✅",
            "cancelled": "❌"
        }.get(status, "❓")
        
        print(f"\n{index}. {status_emoji} {title}")
        print(f"   ID: {task_id}")
        print(f"   Status: {status} ({progress:.0%})")
        print(f"   Agents: {', '.join(agents)}")
    
    def show_task_details(self, task_id: str = None):
        """Show detailed view of a specific task"""
        if not task_id:
            task_id = input("📋 Enter Task ID: ").strip()
            
        try:
            task_dir = Path(self.workspace_path) / "current_tasks" / task_id
            
            if not task_dir.exists():
                print(f"❌ Task {task_id} not found")
                return
            
            # Read task.json
            task_file = task_dir / "task.json"
            if task_file.exists():
                with open(task_file, 'r') as f:
                    task_data = json.load(f)
                
                print(f"\n📋 TASK DETAILS: {task_id}")
                print("=" * 50)
                print(f"Title: {task_data.get('title', 'No title')}")
                print(f"Description: {task_data.get('description', 'No description')}")
                print(f"Status: {task_data.get('status', 'unknown')}")
                print(f"Progress: {task_data.get('progress', 0):.1%}")
                print(f"Created: {task_data.get('created_at', 'unknown')}")
                print(f"Updated: {task_data.get('updated_at', 'unknown')}")
                print(f"Assigned Agents: {', '.join(task_data.get('assigned_agents', []))}")
                
                # Show metadata if available
                metadata_file = task_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    print(f"Priority: {metadata.get('priority', 'unknown')}")
                    print(f"Complexity: {metadata.get('complexity', 'unknown')}")
                
                # Show progress log if available
                progress_file = task_dir / "progress.log"
                if progress_file.exists():
                    print("\n📊 PROGRESS LOG:")
                    print("-" * 20)
                    with open(progress_file, 'r') as f:
                        content = f.read().strip()
                        if content:
                            print(content[-500:])  # Show last 500 characters
                        else:
                            print("No progress logged yet")
            else:
                print(f"❌ Task data not found for {task_id}")
                
        except Exception as e:
            print(f"❌ Error reading task details: {e}")
    
    def live_progress_monitor(self):
        """Live updating progress monitor"""
        print("\n🔄 LIVE PROGRESS MONITOR")
        print("Press Ctrl+C to exit monitor")
        print("=" * 40)
        
        try:
            while True:
                # Clear screen (works on most terminals)
                os.system('clear' if os.name == 'posix' else 'cls')
                
                print("🔄 LIVE PROGRESS MONITOR")
                print(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
                print("=" * 40)
                
                # Show active tasks
                tasks = self.task_manager.list_tasks()
                active_tasks = [t for t in tasks if t.get("status") not in ["completed", "cancelled"]]
                
                if active_tasks:
                    for i, task in enumerate(active_tasks, 1):
                        self.display_task_summary(i, task)
                else:
                    print("📭 No active tasks")
                
                print(f"\n🔄 Refreshing in {self.refresh_interval}s... (Ctrl+C to exit)")
                time.sleep(self.refresh_interval)
                
        except KeyboardInterrupt:
            print("\n👋 Exiting live monitor...")
    
    def view_agent_status(self):
        """Display agent status and health"""
        print("\n🤖 AGENT STATUS")
        print("=" * 30)
        
        # This is a placeholder - in a real implementation, 
        # you'd check actual agent health/status
        agents = [
            {"name": "search_agent", "status": "available", "endpoint": "http://localhost:8001"},
            {"name": "read_write_agent", "status": "available", "endpoint": "http://localhost:8002"}, 
            {"name": "metacognition_agent", "status": "available", "endpoint": "http://localhost:8000"},
        ]
        
        for agent in agents:
            status_emoji = "🟢" if agent["status"] == "available" else "🔴"
            print(f"{status_emoji} {agent['name']}")
            print(f"   Status: {agent['status']}")
            print(f"   Endpoint: {agent['endpoint']}")
            print()
    
    def view_completed_tasks(self):
        """Display completed tasks"""
        print("\n✅ COMPLETED TASKS")
        print("=" * 30)
        
        try:
            # Check completed_tasks directory
            completed_dir = Path(self.workspace_path) / "completed_tasks"
            if not completed_dir.exists():
                print("📭 No completed tasks found")
                return
            
            completed_tasks = list(completed_dir.iterdir())
            if not completed_tasks:
                print("📭 No completed tasks found")
                return
            
            for i, task_dir in enumerate(completed_tasks, 1):
                if task_dir.is_dir():
                    task_file = task_dir / "task.json"
                    if task_file.exists():
                        with open(task_file, 'r') as f:
                            task_data = json.load(f)
                        print(f"{i}. ✅ {task_data.get('title', task_dir.name)}")
                        print(f"   ID: {task_dir.name}")
                        print(f"   Completed: {task_data.get('updated_at', 'unknown')}")
                        print()
                        
        except Exception as e:
            print(f"❌ Error retrieving completed tasks: {e}")
    
    def system_health(self):
        """Display system health and statistics"""
        print("\n🏥 SYSTEM HEALTH")
        print("=" * 30)
        
        try:
            # Workspace statistics
            workspace_path = Path(self.workspace_path)
            current_tasks = len(list((workspace_path / "current_tasks").iterdir())) if (workspace_path / "current_tasks").exists() else 0
            completed_tasks = len(list((workspace_path / "completed_tasks").iterdir())) if (workspace_path / "completed_tasks").exists() else 0
            
            print(f"📁 Workspace: {self.workspace_path}")
            print(f"📋 Current Tasks: {current_tasks}")
            print(f"✅ Completed Tasks: {completed_tasks}")
            print(f"💾 Total Tasks: {current_tasks + completed_tasks}")
            
            # Git status
            try:
                result = subprocess.run(
                    ["git", "status", "--porcelain"], 
                    cwd=self.workspace_path,
                    capture_output=True, 
                    text=True
                )
                if result.returncode == 0:
                    changes = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
                    print(f"🔄 Git Changes: {changes}")
                else:
                    print("🔄 Git Status: Not a git repository")
            except:
                print("🔄 Git Status: Unknown")
            
            print(f"⏰ System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ Error getting system health: {e}")
    
    def run(self):
        """Main CLI loop"""
        try:
            self.display_banner()
            
            while self.running:
                self.display_main_menu()
                
                try:
                    choice = input("\n🎯 Enter your choice (1-8): ").strip()
                    
                    if choice == "1":
                        self.create_task_interactive()
                    elif choice == "2":
                        self.view_active_tasks()
                    elif choice == "3":
                        task_id = input("📋 Enter Task ID (or press Enter to see all): ").strip()
                        if task_id:
                            self.show_task_details(task_id)
                        else:
                            self.view_active_tasks()
                    elif choice == "4":
                        self.view_agent_status()
                    elif choice == "5":
                        self.view_completed_tasks()
                    elif choice == "6":
                        self.live_progress_monitor()
                    elif choice == "7":
                        self.system_health()
                    elif choice == "8":
                        print("\n👋 Goodbye! Shutting down Interface Agent...")
                        self.running = False
                    else:
                        print("❌ Invalid choice. Please enter 1-8.")
                    
                    if self.running and choice != "6":  # Don't pause after live monitor
                        input("\nPress Enter to continue...")
                        
                except KeyboardInterrupt:
                    print("\n\n👋 Goodbye! Shutting down Interface Agent...")
                    self.running = False
                except Exception as e:
                    print(f"❌ Error: {e}")
                    input("Press Enter to continue...")
                    
        except Exception as e:
            print(f"💥 Fatal error: {e}")

def main():
    """Entry point for the interface agent"""
    interface = InterfaceAgent()
    interface.run()

if __name__ == "__main__":
    main() 