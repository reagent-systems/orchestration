"""
Orchestration Interface Agent - Live Task Controller
Textual-based TUI for real-time task management and orchestration monitoring
"""

import os
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dotenv import load_dotenv
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Tree, Static, Button, Input, TextArea, 
    DataTable, Log, Label, ProgressBar, Tabs, TabPane
)
from textual.screen import ModalScreen
from textual.binding import Binding
from textual.reactive import reactive
from textual import events
from rich.text import Text
from rich.console import Console
from rich.syntax import Syntax

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

# Load environment variables from root .env
load_dotenv(dotenv_path="../../.env")

class TaskEditModal(ModalScreen[Dict[str, Any]]):
    """Modal screen for editing task properties"""
    
    def __init__(self, task_data: Dict[str, Any]):
        super().__init__()
        self.task_data = task_data.copy()
    
    def compose(self) -> ComposeResult:
        with Container(classes="modal"):
            yield Label(f"📝 Edit Task: {self.task_data.get('task_id', 'Unknown')}", classes="modal-title")
            
            with Vertical(classes="modal-content"):
                yield Label("Description:")
                yield TextArea(
                    self.task_data.get('description', ''),
                    id="description-input",
                    classes="edit-field"
                )
                
                yield Label("Agent Type:")
                yield Input(
                    value=self.task_data.get('agent_type', ''),
                    placeholder="search, file, terminal, metacognition, etc.",
                    id="agent-type-input",
                    classes="edit-field"
                )
                
                yield Label("Priority (1-5):")
                yield Input(
                    value=str(self.task_data.get('priority', 1)),
                    placeholder="1",
                    id="priority-input",
                    classes="edit-field"
                )
            
            with Horizontal(classes="modal-buttons"):
                yield Button("💾 Save", variant="primary", id="save-btn")
                yield Button("❌ Cancel", variant="error", id="cancel-btn")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            # Collect edited data
            description_widget = self.query_one("#description-input", TextArea)
            agent_type_widget = self.query_one("#agent-type-input", Input) 
            priority_widget = self.query_one("#priority-input", Input)
            
            self.task_data['description'] = description_widget.text
            self.task_data['agent_type'] = agent_type_widget.value
            try:
                self.task_data['priority'] = int(priority_widget.value)
            except ValueError:
                self.task_data['priority'] = 1
                
            self.task_data['modified_at'] = time.time()
            self.dismiss(self.task_data)
        else:
            self.dismiss(None)

class NewTaskModal(ModalScreen[Dict[str, Any]]):
    """Modal screen for creating new tasks"""
    
    def compose(self) -> ComposeResult:
        with Container(classes="modal"):
            yield Label("🆕 Create New Task", classes="modal-title")
            
            with Vertical(classes="modal-content"):
                yield Label("Task Description:")
                yield TextArea(
                    placeholder="Describe what you want the agents to accomplish...",
                    id="new-description-input",
                    classes="edit-field"
                )
                
                yield Label("Preferred Agent Type (optional):")
                yield Input(
                    placeholder="search, file, terminal, metacognition, or leave blank for auto",
                    id="new-agent-type-input",
                    classes="edit-field"
                )
                
                yield Label("Priority (1-5):")
                yield Input(
                    value="3",
                    id="new-priority-input",
                    classes="edit-field"
                )
            
            with Horizontal(classes="modal-buttons"):
                yield Button("✨ Create Task", variant="primary", id="create-btn")
                yield Button("❌ Cancel", variant="error", id="cancel-btn")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create-btn":
            description_widget = self.query_one("#new-description-input", TextArea)
            agent_type_widget = self.query_one("#new-agent-type-input", Input)
            priority_widget = self.query_one("#new-priority-input", Input)
            
            if not description_widget.text.strip():
                return  # Don't create empty tasks
                
            task_data = {
                'description': description_widget.text.strip(),
                'agent_type': agent_type_widget.value.strip() or 'auto',
                'priority': int(priority_widget.value) if priority_widget.value.isdigit() else 3
            }
            
            self.dismiss(task_data)
        else:
            self.dismiss(None)

class WorkspaceWatcher(FileSystemEventHandler):
    """Watches workspace for changes and notifies the interface"""
    
    def __init__(self, interface_app):
        super().__init__()
        self.interface_app = interface_app
    
    def on_any_event(self, event):
        if not event.is_directory:
            # Notify interface of file changes
            self.interface_app.call_from_thread(self.interface_app.refresh_data)

class OrchestrationInterface(App):
    """Main Textual application for orchestration interface"""
    
    CSS = """
    .modal {
        align: center middle;
        background: $panel;
        border: thick $primary;
        padding: 1;
        width: 80;
        height: 20;
    }
    
    .modal-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    
    .modal-content {
        height: auto;
    }
    
    .modal-buttons {
        align: center middle;
        height: 3;
        margin-top: 1;
    }
    
    .edit-field {
        margin-bottom: 1;
    }
    
    .task-tree {
        border: round $primary;
        margin: 1;
    }
    
    .agent-status {
        border: round $secondary;
        margin: 1;
    }
    
    .live-logs {
        border: round $warning;
        margin: 1;
    }
    
    .task-details {
        border: round $success;
        margin: 1;
    }
    
    .status-available { color: $success; }
    .status-claimed { color: $warning; }
    .status-in-progress { color: $primary; }
    .status-completed { color: $accent; }
    .status-failed { color: $error; }
    """
    
    TITLE = "🎛️ Orchestration Control Center"
    SUB_TITLE = "Live Task Management & Agent Monitoring"
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("r", "refresh", "Refresh", priority=True),
        Binding("n", "new_task", "New Task"),
        Binding("e", "edit_task", "Edit Task"),
        Binding("d", "delete_task", "Delete Task"),
        Binding("space", "toggle_task", "Toggle"),
        Binding("tab", "next_panel", "Next Panel"),
    ]
    
    # Reactive properties
    selected_task_id: reactive[str] = reactive("", init=False)
    
    def __init__(self):
        super().__init__()
        self.workspace_path = Path(os.getenv("GIT_WORKSPACE_PATH", "./workspace"))
        self.tasks_path = self.workspace_path / "current_tasks"
        self.agent_id = "interface_agent"
        
        # Data storage
        self.tasks_data: Dict[str, Dict[str, Any]] = {}
        self.agents_status: Dict[str, Dict[str, Any]] = {}
        self.selected_task_path: Optional[Path] = None
        
        # File watcher
        self.observer = Observer()
        self.watcher = WorkspaceWatcher(self)
        
        # Create ADK agent for workspace tools
        self.agent = Agent(
            name="interface_agent",
            model=os.getenv("INTERFACE_MODEL", "gemini-2.0-flash"),
            description="Interface Agent - Live orchestration control center with Textual TUI",
            instruction="""You are the interface agent that provides a live control center for the orchestration system.

Your capabilities:
1. **Live Task Management**: Create, edit, delete, and monitor tasks in real-time
2. **Agent Coordination**: Signal agents about task changes and interruptions
3. **Workspace Monitoring**: Watch for file system changes and agent activity
4. **Interactive Control**: Provide keyboard-driven interface for task manipulation

You provide a sophisticated TUI interface for users to control the orchestration system.""",
            tools=[
                FunctionTool(self.create_task),
                FunctionTool(self.edit_task_file),
                FunctionTool(self.delete_task_file),
                FunctionTool(self.signal_agent_interrupt)
            ]
        )
    
    @FunctionTool
    def create_task(self, description: str, agent_type: str = "auto", priority: int = 3) -> Dict[str, Any]:
        """Create a new task in the workspace"""
        try:
            task_id = f"task-{int(time.time())}-{description[:20].replace(' ', '-').lower()}"
            task_path = self.tasks_path / task_id
            task_path.mkdir(parents=True, exist_ok=True)
            
            task_data = {
                "task_id": task_id,
                "description": description,
                "agent_type": agent_type,
                "status": "available",
                "priority": priority,
                "created_at": time.time(),
                "created_by": "interface_agent",
                "dependencies": []
            }
            
            # Save task
            with open(task_path / "task.json", 'w') as f:
                json.dump(task_data, f, indent=2)
            
            # Initialize progress log
            with open(task_path / "progress.log", 'w') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Task created via Interface Agent\n")
                f.write(f"Description: {description}\n")
                f.write(f"Agent Type: {agent_type}\n")
                f.write(f"Priority: {priority}\n\n")
            
            return {"success": True, "task_id": task_id, "path": str(task_path)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @FunctionTool
    def edit_task_file(self, task_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Edit an existing task and signal any working agents"""
        try:
            task_path = self.tasks_path / task_id
            if not task_path.exists():
                return {"success": False, "error": f"Task {task_id} not found"}
            
            # Load current task
            with open(task_path / "task.json", 'r') as f:
                task_data = json.load(f)
            
            # Check if task is currently being worked on
            working_agent = task_data.get("claimed_by")
            if working_agent and task_data.get("status") == "in_progress":
                # Signal interruption
                self.signal_agent_interrupt(task_id, working_agent)
                task_data["status"] = "available"  # Reset to available
                task_data["claimed_by"] = None
                task_data["claimed_at"] = None
            
            # Apply updates
            for key, value in updates.items():
                if key not in ["task_id", "created_at", "created_by"]:  # Protect immutable fields
                    task_data[key] = value
            
            task_data["modified_at"] = time.time()
            task_data["modified_by"] = "interface_agent"
            
            # Save updated task
            with open(task_path / "task.json", 'w') as f:
                json.dump(task_data, f, indent=2)
            
            # Log the change
            with open(task_path / "progress.log", 'a') as f:
                f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Task modified via Interface Agent\n")
                for key, value in updates.items():
                    f.write(f"  {key}: {value}\n")
                if working_agent:
                    f.write(f"  → Interrupted agent: {working_agent}\n")
            
            return {"success": True, "interrupted_agent": working_agent}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @FunctionTool
    def delete_task_file(self, task_id: str) -> Dict[str, Any]:
        """Delete a task and signal any working agents"""
        try:
            task_path = self.tasks_path / task_id
            if not task_path.exists():
                return {"success": False, "error": f"Task {task_id} not found"}
            
            # Load task to check if it's being worked on
            with open(task_path / "task.json", 'r') as f:
                task_data = json.load(f)
            
            working_agent = task_data.get("claimed_by")
            if working_agent and task_data.get("status") == "in_progress":
                self.signal_agent_interrupt(task_id, working_agent)
            
            # Remove task directory
            import shutil
            shutil.rmtree(task_path)
            
            return {"success": True, "interrupted_agent": working_agent}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @FunctionTool
    def signal_agent_interrupt(self, task_id: str, agent_id: str) -> Dict[str, Any]:
        """Signal an agent to stop working on a task"""
        try:
            # Create interrupt signal file
            interrupt_path = self.workspace_path / "agent_signals" / f"{agent_id}_interrupt_{task_id}.signal"
            interrupt_path.parent.mkdir(exist_ok=True)
            
            with open(interrupt_path, 'w') as f:
                json.dump({
                    "type": "interrupt",
                    "task_id": task_id,
                    "agent_id": agent_id,
                    "timestamp": time.time(),
                    "reason": "task_modified_by_interface"
                }, f, indent=2)
            
            return {"success": True, "signal_file": str(interrupt_path)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def compose(self) -> ComposeResult:
        """Create the main interface layout"""
        yield Header()
        
        with Horizontal():
            # Left panel - Task Tree
            with Vertical(classes="task-tree"):
                yield Label("📋 Task Tree", classes="panel-title")
                yield Tree("Tasks", id="task-tree")
            
            # Middle panel - Agent Status
            with Vertical(classes="agent-status"):
                yield Label("🤖 Agent Status", classes="panel-title")
                yield DataTable(id="agent-table")
            
            # Right panels
            with Vertical():
                # Task details
                with Container(classes="task-details"):
                    yield Label("📄 Task Details", classes="panel-title")
                    yield ScrollableContainer(Static("Select a task to view details...", id="task-details-content"))
                
                # Live logs
                with Container(classes="live-logs"):
                    yield Label("📊 Live Logs", classes="panel-title")
                    yield Log(id="live-log", auto_scroll=True)
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the interface when mounted"""
        # Start file watcher
        if self.tasks_path.exists():
            self.observer.schedule(self.watcher, str(self.tasks_path), recursive=True)
            self.observer.start()
        
        # Setup agent status table
        agent_table = self.query_one("#agent-table", DataTable)
        agent_table.add_columns("Agent", "Status", "Current Task", "Last Active")
        
        # Initial data load
        self.refresh_data()
        
        # Set up auto-refresh
        self.set_interval(2.0, self.refresh_data)
    
    def refresh_data(self) -> None:
        """Refresh all data from workspace"""
        try:
            # Load tasks
            self.load_tasks()
            self.update_task_tree()
            self.update_agent_status()
            self.update_task_details()
            
        except Exception as e:
            log = self.query_one("#live-log", Log)
            log.write_line(f"Error refreshing data: {e}")
    
    def load_tasks(self) -> None:
        """Load all tasks from workspace"""
        self.tasks_data.clear()
        
        if not self.tasks_path.exists():
            return
        
        for task_dir in self.tasks_path.iterdir():
            if task_dir.is_dir():
                task_file = task_dir / "task.json"
                if task_file.exists():
                    try:
                        with open(task_file, 'r') as f:
                            task_data = json.load(f)
                            self.tasks_data[task_data["task_id"]] = task_data
                    except Exception as e:
                        continue
    
    def update_task_tree(self) -> None:
        """Update the task tree display"""
        tree = self.query_one("#task-tree", Tree)
        tree.clear()
        
        if not self.tasks_data:
            tree.root.add_leaf("No tasks available")
            return
        
        # Group tasks by status
        status_groups = {
            "available": [],
            "claimed": [],
            "in_progress": [],
            "completed": [],
            "failed": []
        }
        
        for task_id, task_data in self.tasks_data.items():
            status = task_data.get("status", "unknown")
            if status in status_groups:
                status_groups[status].append((task_id, task_data))
        
        # Add status groups to tree
        for status, tasks in status_groups.items():
            if not tasks:
                continue
                
            status_icons = {
                "available": "⏳",
                "claimed": "🔄", 
                "in_progress": "⚡",
                "completed": "✅",
                "failed": "❌"
            }
            
            status_node = tree.root.add(f"{status_icons.get(status, '?')} {status.upper()} ({len(tasks)})")
            
            for task_id, task_data in tasks:
                description = task_data.get("description", "No description")[:50]
                agent_type = task_data.get("agent_type", "auto")
                claimed_by = task_data.get("claimed_by", "")
                
                label = f"{task_id[:20]}... - {description}"
                if claimed_by:
                    label += f" [{claimed_by}]"
                
                task_node = status_node.add_leaf(label)
                task_node.data = task_id  # Store task ID for selection
    
    def update_agent_status(self) -> None:
        """Update agent status display"""
        agent_table = self.query_one("#agent-table", DataTable)
        agent_table.clear()
        
        # Track agents from tasks
        agents = {}
        current_time = time.time()
        
        for task_data in self.tasks_data.values():
            claimed_by = task_data.get("claimed_by")
            if claimed_by:
                status = task_data.get("status", "unknown")
                claimed_at = task_data.get("claimed_at", current_time)
                
                agents[claimed_by] = {
                    "status": "🔄 Working" if status == "in_progress" else "⏸️ Claimed",
                    "current_task": task_data.get("task_id", "Unknown")[:20],
                    "last_active": time.strftime("%H:%M:%S", time.localtime(claimed_at))
                }
        
        # Add known agents
        known_agents = ["search_agent", "file_operations_agent", "metacognition_agent", 
                       "task_breakdown_agent", "terminal_agent"]
        
        for agent_id in known_agents:
            if agent_id not in agents:
                agents[agent_id] = {
                    "status": "💤 Idle",
                    "current_task": "-",
                    "last_active": "-"
                }
        
        # Populate table
        for agent_id, info in agents.items():
            agent_table.add_row(
                agent_id.replace("_agent", "").title(),
                info["status"],
                info["current_task"],
                info["last_active"]
            )
    
    def update_task_details(self) -> None:
        """Update task details panel"""
        details_widget = self.query_one("#task-details-content", Static)
        
        if not self.selected_task_id or self.selected_task_id not in self.tasks_data:
            details_widget.update("Select a task to view details...")
            return
        
        task_data = self.tasks_data[self.selected_task_id]
        
        # Format task details
        details = []
        details.append(f"🆔 Task ID: {task_data.get('task_id', 'Unknown')}")
        details.append(f"📝 Description: {task_data.get('description', 'No description')}")
        details.append(f"🤖 Agent Type: {task_data.get('agent_type', 'auto')}")
        details.append(f"📊 Status: {task_data.get('status', 'unknown').upper()}")
        details.append(f"⭐ Priority: {task_data.get('priority', 1)}")
        
        if task_data.get("claimed_by"):
            details.append(f"👤 Claimed By: {task_data['claimed_by']}")
            
        if task_data.get("created_at"):
            created_time = datetime.fromtimestamp(task_data["created_at"]).strftime("%Y-%m-%d %H:%M:%S")
            details.append(f"🕐 Created: {created_time}")
            
        if task_data.get("dependencies"):
            details.append(f"🔗 Dependencies: {', '.join(task_data['dependencies'])}")
        
        details_widget.update("\n".join(details))
    
    async def action_new_task(self) -> None:
        """Create a new task"""
        result = await self.push_screen_wait(NewTaskModal())
        if result:
            create_result = self.create_task(
                description=result["description"],
                agent_type=result["agent_type"],
                priority=result["priority"]
            )
            
            log = self.query_one("#live-log", Log)
            if create_result["success"]:
                log.write_line(f"✅ Created task: {create_result['task_id']}")
                self.refresh_data()
            else:
                log.write_line(f"❌ Failed to create task: {create_result['error']}")
    
    async def action_edit_task(self) -> None:
        """Edit the selected task"""
        if not self.selected_task_id or self.selected_task_id not in self.tasks_data:
            log = self.query_one("#live-log", Log)
            log.write_line("⚠️ No task selected for editing")
            return
        
        task_data = self.tasks_data[self.selected_task_id]
        result = await self.push_screen_wait(TaskEditModal(task_data))
        
        if result:
            # Extract only the fields that can be updated
            updates = {
                "description": result["description"],
                "agent_type": result["agent_type"],
                "priority": result["priority"]
            }
            
            edit_result = self.edit_task_file(self.selected_task_id, updates)
            
            log = self.query_one("#live-log", Log)
            if edit_result["success"]:
                log.write_line(f"✅ Updated task: {self.selected_task_id}")
                if edit_result.get("interrupted_agent"):
                    log.write_line(f"🔄 Interrupted agent: {edit_result['interrupted_agent']}")
                self.refresh_data()
            else:
                log.write_line(f"❌ Failed to update task: {edit_result['error']}")
    
    async def action_delete_task(self) -> None:
        """Delete the selected task"""
        if not self.selected_task_id:
            log = self.query_one("#live-log", Log)
            log.write_line("⚠️ No task selected for deletion")
            return
        
        delete_result = self.delete_task_file(self.selected_task_id)
        
        log = self.query_one("#live-log", Log)
        if delete_result["success"]:
            log.write_line(f"🗑️ Deleted task: {self.selected_task_id}")
            if delete_result.get("interrupted_agent"):
                log.write_line(f"🔄 Interrupted agent: {delete_result['interrupted_agent']}")
            self.selected_task_id = ""
            self.refresh_data()
        else:
            log.write_line(f"❌ Failed to delete task: {delete_result['error']}")
    
    def action_refresh(self) -> None:
        """Manually refresh data"""
        log = self.query_one("#live-log", Log)
        log.write_line("🔄 Refreshing data...")
        self.refresh_data()
    
    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle task selection in tree"""
        if hasattr(event.node, 'data') and event.node.data:
            self.selected_task_id = event.node.data
            self.update_task_details()
            
            log = self.query_one("#live-log", Log)
            log.write_line(f"📋 Selected task: {self.selected_task_id}")
    
    def on_unmount(self) -> None:
        """Cleanup when app closes"""
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()

# Create agent instance
interface_agent = OrchestrationInterface()

if __name__ == "__main__":
    interface_agent.run() 