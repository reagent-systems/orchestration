"""
Git-Based Task Tracking System
Maps orchestration steps to git commits for complete task history and progress tracking
"""

import os
import git
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

@dataclass
class TaskStep:
    """Represents a single step in task execution"""
    step_id: str
    task_id: str
    step_number: int
    step_description: str
    agent_name: str
    action_type: str
    parameters: Dict[str, Any]
    result: Dict[str, Any]
    status: str  # pending, in_progress, completed, failed
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[float]
    git_commit_hash: Optional[str]
    dependencies: List[str]
    metadata: Dict[str, Any]

@dataclass
class TaskExecution:
    """Represents a complete task execution"""
    task_id: str
    task_description: str
    user_request: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    status: str  # pending, planning, executing, completed, failed
    total_steps: int
    completed_steps: int
    current_step: int
    completion_percentage: float
    git_branch: str
    git_commits: List[str]
    steps: List[TaskStep]
    metadata: Dict[str, Any]

class GitTaskTracker:
    """Git-based task tracking system"""
    
    def __init__(self, workspace_path: str = "./workspace"):
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(exist_ok=True)
        self.repo = None
        self.task_executions: Dict[str, TaskExecution] = {}
        self.commit_prefix = os.getenv("TASK_COMMIT_PREFIX", "[Orchestration]")
        self.auto_commit = os.getenv("AUTO_COMMIT_TASKS", "true").lower() == "true"
        
        # Setup logging
        self.logger = logging.getLogger("task_tracker")
        
        # Initialize git repository
        self._initialize_git_repo()
    
    def _initialize_git_repo(self):
        """Initialize or connect to git repository for task tracking"""
        try:
            if (self.workspace_path / ".git").exists():
                self.repo = git.Repo(self.workspace_path)
                self.logger.info(f"Connected to existing git repo: {self.repo.working_dir}")
            else:
                # Initialize new repo if TASK_GIT_REPO_URL is provided
                repo_url = os.getenv("TASK_GIT_REPO_URL")
                if repo_url:
                    self.repo = git.Repo.clone_from(repo_url, self.workspace_path)
                    self.logger.info(f"Cloned task git repo from: {repo_url}")
                else:
                    self.repo = git.Repo.init(self.workspace_path)
                    self.logger.info(f"Initialized new task git repo at: {self.workspace_path}")
                
                # Configure git user
                self.repo.config_writer().set_value("user", "name", 
                    os.getenv("GIT_USER_NAME", "Orchestration Agent")).release()
                self.repo.config_writer().set_value("user", "email", 
                    os.getenv("GIT_USER_EMAIL", "orchestration@example.com")).release()
                
                # Create initial commit
                self._create_initial_commit()
                
        except Exception as e:
            self.logger.error(f"Git initialization failed: {e}")
            self.repo = None
    
    def _create_initial_commit(self):
        """Create initial commit for the task repository"""
        try:
            # Create README
            readme_content = """# Task Orchestration History

This repository tracks the execution history of orchestrated tasks.

Each commit represents a step in task execution, providing a complete audit trail of:
- Task planning and decomposition
- Agent assignments and actions
- Progress tracking and updates
- Completion status and results

## Structure
- `tasks/` - Task execution records
- `steps/` - Individual step details
- `metadata/` - System metadata and analytics
"""
            
            readme_path = self.workspace_path / "README.md"
            with open(readme_path, 'w') as f:
                f.write(readme_content)
            
            # Add and commit
            self.repo.index.add([str(readme_path)])
            self.repo.index.commit(f"{self.commit_prefix} Initialize task tracking repository")
            
        except Exception as e:
            self.logger.error(f"Failed to create initial commit: {e}")
    
    def create_task(self, task_description: str, user_request: str, 
                   estimated_steps: int = 10) -> str:
        """Create a new task execution"""
        task_id = str(uuid.uuid4())
        
        # Create task branch
        branch_name = f"task/{task_id[:8]}"
        if self.repo:
            try:
                # Create and checkout new branch
                new_branch = self.repo.create_head(branch_name)
                new_branch.checkout()
                self.logger.info(f"Created task branch: {branch_name}")
            except Exception as e:
                self.logger.error(f"Failed to create task branch: {e}")
                branch_name = "main"
        
        # Create task execution record
        task_execution = TaskExecution(
            task_id=task_id,
            task_description=task_description,
            user_request=user_request,
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            status="pending",
            total_steps=estimated_steps,
            completed_steps=0,
            current_step=0,
            completion_percentage=0.0,
            git_branch=branch_name,
            git_commits=[],
            steps=[],
            metadata={
                "estimated_steps": estimated_steps,
                "created_by": "metacognition_agent"
            }
        )
        
        self.task_executions[task_id] = task_execution
        
        # Create task directory and files
        self._create_task_files(task_id, task_execution)
        
        # Commit task creation
        if self.auto_commit and self.repo:
            self._commit_task_creation(task_id, task_execution)
        
        self.logger.info(f"Created task: {task_id} - {task_description}")
        return task_id
    
    def start_task(self, task_id: str) -> bool:
        """Start task execution"""
        if task_id not in self.task_executions:
            return False
        
        task = self.task_executions[task_id]
        task.status = "planning"
        task.started_at = datetime.now()
        
        # Update task files
        self._update_task_files(task_id, task)
        
        # Commit task start
        if self.auto_commit and self.repo:
            self._commit_task_update(task_id, "Start task execution", task)
        
        self.logger.info(f"Started task: {task_id}")
        return True
    
    def add_task_step(self, task_id: str, step_description: str, agent_name: str, 
                     action_type: str, parameters: Dict[str, Any] = None) -> str:
        """Add a new step to a task"""
        if task_id not in self.task_executions:
            return None
        
        task = self.task_executions[task_id]
        step_id = str(uuid.uuid4())
        
        # Create step record
        step = TaskStep(
            step_id=step_id,
            task_id=task_id,
            step_number=len(task.steps) + 1,
            step_description=step_description,
            agent_name=agent_name,
            action_type=action_type,
            parameters=parameters or {},
            result={},
            status="pending",
            start_time=datetime.now(),
            end_time=None,
            duration=None,
            git_commit_hash=None,
            dependencies=[],
            metadata={}
        )
        
        task.steps.append(step)
        task.total_steps = len(task.steps)
        
        # Update task files
        self._update_task_files(task_id, task)
        
        # Commit step addition
        if self.auto_commit and self.repo:
            self._commit_task_update(task_id, f"Add step {step.step_number}: {step_description}", task)
        
        self.logger.info(f"Added step {step.step_number} to task {task_id}: {step_description}")
        return step_id
    
    def update_step_status(self, task_id: str, step_id: str, status: str, 
                          result: Dict[str, Any] = None, metadata: Dict[str, Any] = None) -> bool:
        """Update the status of a task step"""
        if task_id not in self.task_executions:
            return False
        
        task = self.task_executions[task_id]
        step = next((s for s in task.steps if s.step_id == step_id), None)
        
        if not step:
            return False
        
        step.status = status
        if result:
            step.result.update(result)
        if metadata:
            step.metadata.update(metadata)
        
        if status in ["completed", "failed"]:
            step.end_time = datetime.now()
            step.duration = (step.end_time - step.start_time).total_seconds()
            
            # Update completion percentage
            completed_steps = len([s for s in task.steps if s.status == "completed"])
            task.completed_steps = completed_steps
            task.completion_percentage = (completed_steps / len(task.steps)) * 100 if task.steps else 0
            
            # Check if task is complete
            if completed_steps == len(task.steps):
                task.status = "completed"
                task.completed_at = datetime.now()
        
        # Update task files
        self._update_task_files(task_id, task)
        
        # Commit step update
        if self.auto_commit and self.repo:
            commit_message = f"Step {step.step_number} {status}: {step.step_description}"
            self._commit_task_update(task_id, commit_message, task)
            step.git_commit_hash = self.repo.head.commit.hexsha
        
        self.logger.info(f"Updated step {step.step_number} status to {status} for task {task_id}")
        return True
    
    def complete_task(self, task_id: str, final_result: Dict[str, Any] = None) -> bool:
        """Mark a task as completed"""
        if task_id not in self.task_executions:
            return False
        
        task = self.task_executions[task_id]
        task.status = "completed"
        task.completed_at = datetime.now()
        task.completion_percentage = 100.0
        
        if final_result:
            task.metadata["final_result"] = final_result
        
        # Update task files
        self._update_task_files(task_id, task)
        
        # Commit task completion
        if self.auto_commit and self.repo:
            self._commit_task_update(task_id, "Complete task execution", task)
        
        self.logger.info(f"Completed task: {task_id}")
        return True
    
    def fail_task(self, task_id: str, error_message: str, error_details: Dict[str, Any] = None) -> bool:
        """Mark a task as failed"""
        if task_id not in self.task_executions:
            return False
        
        task = self.task_executions[task_id]
        task.status = "failed"
        task.completed_at = datetime.now()
        
        task.metadata["error"] = {
            "message": error_message,
            "details": error_details or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Update task files
        self._update_task_files(task_id, task)
        
        # Commit task failure
        if self.auto_commit and self.repo:
            self._commit_task_update(task_id, f"Task failed: {error_message}", task)
        
        self.logger.error(f"Failed task: {task_id} - {error_message}")
        return True
    
    def _create_task_files(self, task_id: str, task: TaskExecution):
        """Create files for task tracking"""
        task_dir = self.workspace_path / "tasks" / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        
        # Create task metadata file
        metadata_file = task_dir / "task.json"
        with open(metadata_file, 'w') as f:
            json.dump(asdict(task), f, indent=2, default=str)
        
        # Create steps directory
        steps_dir = task_dir / "steps"
        steps_dir.mkdir(exist_ok=True)
        
        # Create progress file
        progress_file = task_dir / "progress.json"
        progress_data = {
            "task_id": task_id,
            "status": task.status,
            "completion_percentage": task.completion_percentage,
            "current_step": task.current_step,
            "total_steps": task.total_steps,
            "last_update": datetime.now().isoformat()
        }
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2, default=str)
    
    def _update_task_files(self, task_id: str, task: TaskExecution):
        """Update task tracking files"""
        task_dir = self.workspace_path / "tasks" / task_id
        
        # Update task metadata
        metadata_file = task_dir / "task.json"
        with open(metadata_file, 'w') as f:
            json.dump(asdict(task), f, indent=2, default=str)
        
        # Update progress
        progress_file = task_dir / "progress.json"
        progress_data = {
            "task_id": task_id,
            "status": task.status,
            "completion_percentage": task.completion_percentage,
            "current_step": task.current_step,
            "total_steps": task.total_steps,
            "last_update": datetime.now().isoformat()
        }
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2, default=str)
        
        # Update individual step files
        steps_dir = task_dir / "steps"
        for step in task.steps:
            step_file = steps_dir / f"step_{step.step_number:03d}.json"
            with open(step_file, 'w') as f:
                json.dump(asdict(step), f, indent=2, default=str)
    
    def _commit_task_creation(self, task_id: str, task: TaskExecution):
        """Commit task creation to git"""
        try:
            task_dir = self.workspace_path / "tasks" / task_id
            self.repo.index.add([str(task_dir)])
            
            commit_message = f"{self.commit_prefix} Create task: {task.task_description[:50]}"
            self.repo.index.commit(commit_message)
            
            task.git_commits.append(self.repo.head.commit.hexsha)
            
        except Exception as e:
            self.logger.error(f"Failed to commit task creation: {e}")
    
    def _commit_task_update(self, task_id: str, message: str, task: TaskExecution):
        """Commit task update to git"""
        try:
            task_dir = self.workspace_path / "tasks" / task_id
            self.repo.index.add([str(task_dir)])
            
            commit_message = f"{self.commit_prefix} {message}"
            self.repo.index.commit(commit_message)
            
            task.git_commits.append(self.repo.head.commit.hexsha)
            
        except Exception as e:
            self.logger.error(f"Failed to commit task update: {e}")
    
    def get_task(self, task_id: str) -> Optional[TaskExecution]:
        """Get a task execution by ID"""
        return self.task_executions.get(task_id)
    
    def get_active_tasks(self) -> List[TaskExecution]:
        """Get all active tasks"""
        return [t for t in self.task_executions.values() if t.status in ["pending", "planning", "executing"]]
    
    def get_completed_tasks(self, days: int = 30) -> List[TaskExecution]:
        """Get completed tasks from the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [t for t in self.task_executions.values() 
                if t.status == "completed" and t.completed_at and t.completed_at > cutoff_date]
    
    def get_task_history(self, task_id: str) -> List[Dict[str, Any]]:
        """Get git history for a specific task"""
        if not self.repo or task_id not in self.task_executions:
            return []
        
        task = self.task_executions[task_id]
        history = []
        
        try:
            # Get commits for this task
            for commit_hash in task.git_commits:
                commit = self.repo.commit(commit_hash)
                history.append({
                    "commit_hash": commit_hash,
                    "message": commit.message,
                    "author": commit.author.name,
                    "timestamp": commit.committed_datetime.isoformat(),
                    "files_changed": list(commit.stats.files.keys())
                })
        except Exception as e:
            self.logger.error(f"Failed to get task history: {e}")
        
        return history
    
    def export_task_data(self, task_id: str) -> Dict[str, Any]:
        """Export complete task data"""
        if task_id not in self.task_executions:
            return {}
        
        task = self.task_executions[task_id]
        return {
            "task": asdict(task),
            "history": self.get_task_history(task_id),
            "export_timestamp": datetime.now().isoformat()
        }
    
    def cleanup_old_tasks(self, days: int = None):
        """Clean up old task data"""
        if days is None:
            days = int(os.getenv("TASK_HISTORY_RETENTION_DAYS", "30"))
        
        cutoff_date = datetime.now() - timedelta(days=days)
        tasks_to_remove = []
        
        for task_id, task in self.task_executions.items():
            if task.completed_at and task.completed_at < cutoff_date:
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            # Remove task files
            task_dir = self.workspace_path / "tasks" / task_id
            if task_dir.exists():
                import shutil
                shutil.rmtree(task_dir)
            
            # Remove from memory
            del self.task_executions[task_id]
        
        if tasks_to_remove:
            self.logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")

# Global task tracker instance
task_tracker = GitTaskTracker(os.getenv("TASK_WORKSPACE_PATH", "./workspace")) 