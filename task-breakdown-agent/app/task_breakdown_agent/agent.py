"""
Task Breakdown Agent
Specialized ADK agent that decomposes complex tasks into sequential steps
"""

import os
import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

class TaskBreakdownAgent(Agent):
    """Specialized agent for breaking down complex tasks into manageable sequential steps"""
    
    def __init__(self, name: str = "task_breakdown_agent", model: str = None):
        # Single-purpose tools - only task breakdown
        tools = [
            FunctionTool(self.breakdown_complex_task)
        ]
        
        super().__init__(
            name=name,
            model=model or os.getenv("TASK_BREAKDOWN_MODEL", "gemini-2.0-flash-live-001"),
            description="Task breakdown specialist that decomposes complex tasks into sequential steps",
            instruction="""You are a task breakdown specialist. Your ONLY job is to take complex tasks and break them down into sequential, manageable steps.

When you see a complex task:
1. Analyze what the task requires
2. Break it into 3-7 sequential steps
3. Identify which type of agent each step needs
4. Create clear, actionable subtasks
5. Set up proper dependencies between steps

Example:
Complex task: "analyze codebase for syntax flaws and compare with fixes from Stack Overflow"
Your breakdown:
1. "Plan codebase analysis strategy" (needs_planning: true, agent_type: planning)
2. "Execute codebase analysis based on plan" (depends_on: step-1, agent_type: terminal)  
3. "Research syntax error fixes on Stack Overflow" (depends_on: step-2, agent_type: search)
4. "Apply selected fixes to codebase" (depends_on: step-3, agent_type: file_operations)

Keep it simple, sequential, and clear.""",
            tools=tools
        )
        
        # Store workspace path in global scope since ADK Agent doesn't allow custom attributes
        global workspace_path, current_tasks_dir
        workspace_path = Path(os.getenv("TASK_WORKSPACE_PATH", "./workspace"))
        current_tasks_dir = workspace_path / "current_tasks"
    
    async def breakdown_complex_task(self, task_description: str, task_id: str = None) -> Dict[str, Any]:
        """Break down a complex task into sequential steps
        
        Args:
            task_description: The complex task to break down
            task_id: Optional existing task ID, will create new if not provided
            
        Returns:
            Dict containing breakdown results and created subtasks
        """
        try:
            # Create task ID if not provided
            if not task_id:
                task_id = f"breakdown-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"
            
            # Analyze the task and create breakdown
            breakdown_analysis = self._analyze_task_complexity(task_description)
            sequential_steps = self._create_sequential_steps(task_description, breakdown_analysis)
            
            # Create subtasks in workspace
            created_subtasks = []
            for i, step in enumerate(sequential_steps):
                subtask_id = f"{task_id}-step-{i+1:02d}"
                subtask = self._create_subtask(subtask_id, step, i == 0)  # First step has no dependencies
                created_subtasks.append(subtask)
                
                # Save subtask to workspace
                self._save_subtask_to_workspace(subtask)
            
            # Log the breakdown
            breakdown_result = {
                "success": True,
                "original_task": task_description,
                "parent_task_id": task_id,
                "total_steps": len(sequential_steps),
                "subtasks_created": created_subtasks,
                "breakdown_strategy": breakdown_analysis["strategy"],
                "estimated_completion_time": breakdown_analysis["estimated_minutes"]
            }
            
            print(f"✅ Task breakdown complete: {len(sequential_steps)} steps created for '{task_description[:50]}...'")
            return breakdown_result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Task breakdown failed: {str(e)}",
                "original_task": task_description
            }
            print(f"❌ Task breakdown failed: {e}")
            return error_result
    
    def _analyze_task_complexity(self, task_description: str) -> Dict[str, Any]:
        """Analyze task to determine breakdown strategy"""
        task_lower = task_description.lower()
        
        # Determine complexity and strategy based on keywords
        if any(keyword in task_lower for keyword in ["analyze", "compare", "research"]):
            strategy = "analysis_workflow"
            estimated_minutes = 15
            complexity = "high"
        elif any(keyword in task_lower for keyword in ["search", "find", "gather"]):
            strategy = "information_gathering"
            estimated_minutes = 8
            complexity = "medium"
        elif any(keyword in task_lower for keyword in ["create", "write", "generate"]):
            strategy = "creation_workflow"
            estimated_minutes = 10
            complexity = "medium"
        else:
            strategy = "general_workflow"
            estimated_minutes = 12
            complexity = "medium"
        
        return {
            "strategy": strategy,
            "complexity": complexity,
            "estimated_minutes": estimated_minutes,
            "requires_planning": "plan" in task_lower or "strategy" in task_lower or complexity == "high"
        }
    
    def _create_sequential_steps(self, task_description: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create sequential steps based on task analysis"""
        steps = []
        
        if analysis["strategy"] == "analysis_workflow":
            # Example: "analyze codebase for syntax flaws and compare with fixes from Stack Overflow"
            steps = [
                {
                    "description": f"Plan analysis strategy for: {task_description}",
                    "agent_type": "planning",
                    "needs_planning": True,  
                    "estimated_minutes": 3
                },
                {
                    "description": f"Execute analysis based on plan",
                    "agent_type": "terminal",
                    "needs_planning": False,
                    "estimated_minutes": 8
                },
                {
                    "description": f"Research solutions and fixes for found issues",
                    "agent_type": "search", 
                    "needs_planning": False,
                    "estimated_minutes": 6
                },
                {
                    "description": f"Apply selected solutions",
                    "agent_type": "file_operations",
                    "needs_planning": False,
                    "estimated_minutes": 4
                }
            ]
        elif analysis["strategy"] == "information_gathering":
            steps = [
                {  
                    "description": f"Search and gather information: {task_description}",
                    "agent_type": "search",
                    "needs_planning": False,
                    "estimated_minutes": 5
                },
                {
                    "description": f"Organize and save gathered information",
                    "agent_type": "file_operations",
                    "needs_planning": False, 
                    "estimated_minutes": 3
                }
            ]
        elif analysis["strategy"] == "creation_workflow":
            steps = [
                {
                    "description": f"Plan creation approach for: {task_description}",
                    "agent_type": "planning",
                    "needs_planning": True,
                    "estimated_minutes": 4
                },
                {
                    "description": f"Create content based on plan",
                    "agent_type": "file_operations",
                    "needs_planning": False,
                    "estimated_minutes": 6
                }
            ]
        else:
            # General workflow
            steps = [
                {
                    "description": f"Plan approach for: {task_description}",
                    "agent_type": "planning", 
                    "needs_planning": True,
                    "estimated_minutes": 4
                },
                {
                    "description": f"Execute planned approach",
                    "agent_type": "terminal",
                    "needs_planning": False,
                    "estimated_minutes": 8
                }
            ]
        
        return steps
    
    def _create_subtask(self, subtask_id: str, step: Dict[str, Any], is_first_step: bool) -> Dict[str, Any]:
        """Create a subtask from a step definition"""
        return {
            "task_id": subtask_id,
            "title": step["description"],
            "description": step["description"],
            "created_by": self.name,
            "agent_type": step["agent_type"],
            "needs_planning": step.get("needs_planning", False),
            "status": "available" if is_first_step else "blocked",
            "progress": 0.0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "estimated_minutes": step.get("estimated_minutes", 5),
            "dependencies": [] if is_first_step else [f"previous_step"],
            "blockers": [],
            "next_actions": [],
            "metadata": {
                "created_by_breakdown": True,
                "step_type": step["agent_type"],
                "breakdown_agent": self.name
            }
        }
    
    def _save_subtask_to_workspace(self, subtask: Dict[str, Any]):
        """Save subtask to workspace for other agents to find"""
        try:
            task_dir = current_tasks_dir / subtask["task_id"] 
            task_dir.mkdir(parents=True, exist_ok=True)
            
            # Save task metadata
            task_file = task_dir / "task.json"
            with open(task_file, 'w') as f:
                json.dump(subtask, f, indent=2)
            
            # Create progress log
            progress_file = task_dir / "progress.log"
            with open(progress_file, 'w') as f:
                f.write(f"=== Subtask Created: {datetime.now().isoformat()} ===\n")
                f.write(f"Task: {subtask['title']}\n")
                f.write(f"Type: {subtask['agent_type']}\n")
                f.write(f"Status: {subtask['status']}\n")
                f.write(f"Created by: {self.name}\n\n")
                
            print(f"📝 Created subtask: {subtask['task_id']}")
            
        except Exception as e:
            print(f"❌ Failed to save subtask {subtask['task_id']}: {e}")
    
    async def monitor_workspace(self):
        """Monitor workspace for complex tasks that need breakdown"""
        print(f"🔍 {self.name} monitoring workspace for complex tasks...")
        
        while True:
            try:
                complex_tasks = self._find_complex_tasks()
                
                for task in complex_tasks:
                    print(f"🧩 Found complex task: {task['task_id']}")
                    self._claim_task(task)
                    
                    # Break down the task
                    result = await self.breakdown_complex_task(
                        task['description'], 
                        task['task_id']
                    )
                    
                    if result.get("success"):
                        self._mark_task_completed(task)
                        print(f"✅ Completed breakdown of {task['task_id']}")
                    else:
                        print(f"❌ Failed to break down {task['task_id']}")
                
                await asyncio.sleep(3)  # Check every 3 seconds
                
            except Exception as e:
                print(f"❌ Error in workspace monitoring: {e}")
                await asyncio.sleep(5)
    
    def _find_complex_tasks(self) -> List[Dict[str, Any]]:
        """Find tasks that need breakdown (complex, unassigned tasks)"""
        complex_tasks = []
        
        try:
            if not current_tasks_dir.exists():
                return complex_tasks
                
            for task_dir in current_tasks_dir.iterdir():
                if not task_dir.is_dir():
                    continue
                    
                task_file = task_dir / "task.json"
                if not task_file.exists():
                    continue
                
                with open(task_file, 'r') as f:
                    task = json.load(f)
                
                # Look for tasks that:
                # 1. Are complex (multiple actions implied)
                # 2. Haven't been broken down yet
                # 3. Are available or not_started
                if (self._is_complex_task(task) and 
                    not task.get("metadata", {}).get("created_by_breakdown", False) and
                    task.get("status") in ["available", "not_started"] and
                    not self._is_task_claimed(task)):
                    
                    complex_tasks.append(task)
                    
        except Exception as e:
            print(f"❌ Error finding complex tasks: {e}")
        
        return complex_tasks
    
    def _is_complex_task(self, task: Dict[str, Any]) -> bool:
        """Determine if a task is complex and needs breakdown"""
        description = task.get("description", "").lower()
        
        # Complex task indicators
        complexity_indicators = [
            " and ",  # Multiple actions: "analyze and compare"
            "compare",  # Comparison tasks are usually complex
            "analyze",  # Analysis tasks need planning
            "research and",  # Research + action
            "find and",  # Find + action  
            "create comprehensive",  # Comprehensive tasks
            "full analysis",  # Full analysis tasks
            "step by step",  # Explicitly multi-step
        ]
        
        return any(indicator in description for indicator in complexity_indicators)
    
    def _is_task_claimed(self, task: Dict[str, Any]) -> bool:
        """Check if task is already claimed by an agent"""
        return task.get("status") in ["claimed", "in_progress", "completed"]
    
    def _claim_task(self, task: Dict[str, Any]):
        """Claim a task by updating its status"""
        try:
            task["status"] = "claimed"
            task["claimed_by"] = self.name
            task["claimed_at"] = datetime.now().isoformat()
            
            task_dir = current_tasks_dir / task["task_id"]
            task_file = task_dir / "task.json"
            
            with open(task_file, 'w') as f:
                json.dump(task, f, indent=2)
                
        except Exception as e:
            print(f"❌ Failed to claim task {task['task_id']}: {e}")
    
    def _mark_task_completed(self, task: Dict[str, Any]):
        """Mark a task as completed"""
        try:
            task["status"] = "completed"
            task["completed_by"] = self.name
            task["completed_at"] = datetime.now().isoformat()
            
            task_dir = current_tasks_dir / task["task_id"]
            task_file = task_dir / "task.json"
            
            with open(task_file, 'w') as f:
                json.dump(task, f, indent=2)
                
        except Exception as e:
            print(f"❌ Failed to mark task completed {task['task_id']}: {e}")

# Create the agent instance
task_breakdown_agent = TaskBreakdownAgent()

if __name__ == "__main__":
    async def main():
        """Main entry point for the task breakdown agent"""
        print("🧩 Starting Task Breakdown Agent...")
        print("Specialization: Complex task decomposition")
        print("Framework: Google ADK")
        print("Workspace monitoring: ENABLED")
        
        # Start monitoring workspace
        await task_breakdown_agent.monitor_workspace()
    
    asyncio.run(main()) 