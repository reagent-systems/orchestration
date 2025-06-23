"""
Metacognition Agent - Task Expansion Specialist
Specialized ADK agent that expands tasks requiring detailed planning and detects/resolves stuck tasks
"""

import os
import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

class MetacognitionAgent(Agent):
    """Specialized agent for task expansion, detailed planning, and stuck task resolution"""
    
    def __init__(self, name: str = "metacognition_agent", model: str = None):
        # Single-purpose tools - only planning and task expansion
        tools = [
            FunctionTool(self.expand_planning_task),
            FunctionTool(self.create_detailed_plan),
            FunctionTool(self.resolve_stuck_task)
        ]
        
        super().__init__(
            name=name,
            model=model or os.getenv("METACOGNITION_MODEL", "gemini-2.0-flash-live-001"),
            description="Task expansion specialist for detailed planning and stuck task resolution",
            instruction="""You are a task expansion and planning specialist. Your ONLY job is to take high-level tasks that need planning and expand them into detailed, executable steps.

Your specializations:
1. **Task Expansion**: Take vague planning tasks and create specific, actionable steps
2. **Detailed Planning**: Create comprehensive execution strategies with specific commands/approaches
3. **Stuck Task Resolution**: Detect loops and create alternative approaches when tasks fail repeatedly

When you see a task that needs planning:
1. Analyze what the task requires in detail
2. Create specific, executable steps with concrete commands/approaches
3. Consider context from previous steps and available information
4. Provide alternative approaches if the primary plan might fail

Example:
Input: "Plan analysis strategy for: analyze codebase for syntax flaws"
Your expansion:
1. "Identify file types in codebase using find command"
2. "Choose appropriate linting tools (pylint for .py, eslint for .js)"  
3. "Define specific error patterns to search for"
4. "Create command sequence for systematic analysis"

Keep it practical, specific, and executable.""",
            tools=tools
        )
        
        self.workspace_path = Path(os.getenv("TASK_WORKSPACE_PATH", "./workspace"))
        self.current_tasks_dir = self.workspace_path / "current_tasks"
        
        # Track task attempts to detect loops
        self.task_attempts = {}
    
    async def expand_planning_task(self, task_description: str, task_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Expand a planning task into detailed, executable steps
        
        Args:
            task_description: The planning task to expand
            task_id: ID of the task being expanded
            context: Additional context from previous steps or workspace
            
        Returns:
            Dict containing expanded steps and execution plan
        """
        try:
            print(f"🧠 Expanding planning task: {task_description}")
            
            # Analyze the planning requirements
            planning_analysis = self._analyze_planning_requirements(task_description, context or {})
            
            # Create detailed execution plan
            detailed_steps = self._create_detailed_execution_plan(task_description, planning_analysis)
            
            # Create subtasks for the detailed steps
            created_subtasks = []
            for i, step in enumerate(detailed_steps):
                subtask_id = f"{task_id}-detail-{i+1:02d}"
                subtask = self._create_execution_subtask(subtask_id, step, i == 0)
                created_subtasks.append(subtask)
                
                # Save subtask to workspace
                self._save_subtask_to_workspace(subtask)
            
            # Mark original planning task as completed
            self._mark_planning_task_completed(task_id, detailed_steps)
            
            expansion_result = {
                "success": True,
                "original_task": task_description,
                "task_id": task_id,
                "planning_analysis": planning_analysis,
                "detailed_steps": len(detailed_steps),
                "subtasks_created": created_subtasks,
                "execution_strategy": planning_analysis["strategy"]
            }
            
            print(f"✅ Planning expansion complete: {len(detailed_steps)} detailed steps created")
            return expansion_result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Planning expansion failed: {str(e)}",
                "original_task": task_description,
                "task_id": task_id
            }
            print(f"❌ Planning expansion failed: {e}")
            return error_result
    
    async def create_detailed_plan(self, objective: str, available_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a detailed execution plan for a specific objective
        
        Args:
            objective: What needs to be accomplished
            available_info: Information available from previous steps
            
        Returns:
            Dict containing detailed plan with specific commands and approaches
        """
        try:
            # Determine the type of planning needed
            if "analysis" in objective.lower():
                plan = self._create_analysis_plan(objective, available_info or {})
            elif "search" in objective.lower() or "research" in objective.lower():
                plan = self._create_research_plan(objective, available_info or {})
            elif "file" in objective.lower() or "code" in objective.lower():
                plan = self._create_file_operation_plan(objective, available_info or {})
            else:
                plan = self._create_general_plan(objective, available_info or {})
            
            return {
                "success": True,
                "objective": objective,
                "plan": plan,
                "plan_type": plan["type"],
                "estimated_duration": plan["estimated_minutes"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Plan creation failed: {str(e)}",
                "objective": objective
            }
    
    async def resolve_stuck_task(self, task_id: str, failure_context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve a stuck task by creating alternative approaches
        
        Args:
            task_id: ID of the stuck task
            failure_context: Information about why the task is stuck
            
        Returns:
            Dict containing alternative approach and resolution steps
        """
        try:
            print(f"🔄 Resolving stuck task: {task_id}")
            
            # Track attempts to detect patterns
            if task_id not in self.task_attempts:
                self.task_attempts[task_id] = []
            
            self.task_attempts[task_id].append({
                "timestamp": datetime.now().isoformat(),
                "failure_context": failure_context
            })
            
            # Analyze failure pattern
            failure_analysis = self._analyze_failure_pattern(task_id, failure_context)
            
            # Create alternative approach
            alternative = self._create_alternative_approach(task_id, failure_analysis)
            
            # Create new subtask with alternative approach
            alt_task_id = f"{task_id}-alt-{len(self.task_attempts[task_id])}"
            alt_subtask = self._create_alternative_subtask(alt_task_id, alternative)
            
            # Save alternative subtask
            self._save_subtask_to_workspace(alt_subtask)
            
            resolution_result = {
                "success": True,
                "original_task_id": task_id,
                "alternative_task_id": alt_task_id,
                "failure_analysis": failure_analysis,
                "alternative_approach": alternative,
                "attempt_number": len(self.task_attempts[task_id])
            }
            
            print(f"✅ Alternative approach created: {alternative['strategy']}")
            return resolution_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Stuck task resolution failed: {str(e)}",
                "task_id": task_id
            }
    
    def _analyze_planning_requirements(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze what type of detailed planning is needed"""
        task_lower = task_description.lower()
        
        if "codebase" in task_lower and "analysis" in task_lower:
            return {
                "strategy": "codebase_analysis",
                "requires": ["file_discovery", "tool_selection", "pattern_definition"],
                "estimated_minutes": 8,
                "complexity": "high"
            }
        elif "plan" in task_lower and "strategy" in task_lower:
            return {
                "strategy": "strategic_planning", 
                "requires": ["objective_analysis", "approach_selection", "step_sequencing"],
                "estimated_minutes": 5,
                "complexity": "medium"
            }
        elif "research" in task_lower:
            return {
                "strategy": "research_planning",
                "requires": ["keyword_identification", "source_selection", "search_strategy"],
                "estimated_minutes": 4,
                "complexity": "medium"
            }
        else:
            return {
                "strategy": "general_planning",
                "requires": ["requirement_analysis", "approach_definition"],
                "estimated_minutes": 6,
                "complexity": "medium"
            }
    
    def _create_detailed_execution_plan(self, task_description: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create detailed execution steps based on planning analysis"""
        steps = []
        
        if analysis["strategy"] == "codebase_analysis":
            steps = [
                {
                    "description": "Identify file types and structure in codebase",
                    "agent_type": "terminal",
                    "specific_commands": ["find . -type f -name '*.py' | head -20", "find . -type f -name '*.js' | head -20"],
                    "expected_output": "List of Python and JavaScript files",
                    "estimated_minutes": 2
                },
                {
                    "description": "Select appropriate linting tools based on file types found",
                    "agent_type": "planning",
                    "needs_planning": True,
                    "decision_criteria": "File types from previous step",
                    "estimated_minutes": 2
                },
                {
                    "description": "Define specific syntax error patterns to search for",
                    "agent_type": "planning", 
                    "needs_planning": True,
                    "focus": "Common syntax errors, undefined variables, import issues",
                    "estimated_minutes": 2
                },
                {
                    "description": "Execute systematic syntax analysis using selected tools",
                    "agent_type": "terminal",
                    "depends_on_planning": True,
                    "estimated_minutes": 4
                }
            ]
        elif analysis["strategy"] == "research_planning":
            steps = [
                {
                    "description": "Identify key search terms and keywords",
                    "agent_type": "planning",
                    "needs_planning": True,
                    "focus": "Extract main concepts and technical terms",
                    "estimated_minutes": 2
                },
                {
                    "description": "Select optimal information sources",
                    "agent_type": "planning",
                    "needs_planning": True, 
                    "options": "Stack Overflow, GitHub, documentation sites",
                    "estimated_minutes": 1
                },
                {
                    "description": "Execute targeted research with defined strategy",
                    "agent_type": "search",
                    "depends_on_planning": True,
                    "estimated_minutes": 5
                }
            ]
        else:
            # General planning steps
            steps = [
                {
                    "description": "Analyze specific requirements and constraints",
                    "agent_type": "planning",
                    "needs_planning": True,
                    "estimated_minutes": 3
                },
                {
                    "description": "Execute planned approach",
                    "agent_type": "terminal",
                    "depends_on_planning": True,
                    "estimated_minutes": 5
                }
            ]
        
        return steps
    
    def _create_analysis_plan(self, objective: str, available_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed analysis plan"""
        return {
            "type": "analysis",
            "objective": objective,
            "approach": "systematic_analysis",
            "steps": [
                "Identify analysis scope and boundaries",
                "Select appropriate analysis tools",
                "Define success criteria",
                "Execute analysis systematically",
                "Validate and document results"
            ],
            "tools_suggested": ["find", "grep", "awk", "statistical tools"],
            "estimated_minutes": 10
        }
    
    def _create_research_plan(self, objective: str, available_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed research plan"""
        return {
            "type": "research",
            "objective": objective,
            "approach": "targeted_search",
            "steps": [
                "Extract key terms and concepts",
                "Identify authoritative sources",
                "Develop search queries",
                "Execute searches systematically",
                "Synthesize and validate findings"
            ],
            "sources_suggested": ["Stack Overflow", "GitHub", "official documentation"],
            "estimated_minutes": 8
        }
    
    def _create_file_operation_plan(self, objective: str, available_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed file operation plan"""
        return {
            "type": "file_operations",
            "objective": objective,
            "approach": "safe_file_handling",
            "steps": [
                "Identify target files and directories",
                "Create backup strategy",
                "Plan modification approach",
                "Execute changes incrementally",
                "Verify changes and commit"
            ],
            "safety_measures": ["backup_creation", "incremental_changes", "validation"],
            "estimated_minutes": 12
        }
    
    def _create_general_plan(self, objective: str, available_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create general execution plan"""
        return {
            "type": "general",
            "objective": objective,
            "approach": "structured_execution",
            "steps": [
                "Define clear requirements",
                "Break down into manageable parts",
                "Plan execution sequence",
                "Execute with monitoring",
                "Validate results"
            ],
            "estimated_minutes": 8
        }
    
    def _analyze_failure_pattern(self, task_id: str, failure_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze why a task is failing repeatedly"""
        attempts = self.task_attempts.get(task_id, [])
        
        if len(attempts) >= 3:
            pattern = "chronic_failure"
            recommendation = "fundamental_approach_change"
        elif "timeout" in str(failure_context).lower():
            pattern = "timeout_issues"
            recommendation = "simplify_or_parallelize"
        elif "not_found" in str(failure_context).lower():
            pattern = "resource_unavailable"
            recommendation = "alternative_sources"
        else:
            pattern = "execution_error"
            recommendation = "different_tool_or_method"
        
        return {
            "pattern": pattern,
            "attempts": len(attempts),
            "recommendation": recommendation,
            "severity": "high" if len(attempts) >= 3 else "medium"
        }
    
    def _create_alternative_approach(self, task_id: str, failure_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create alternative approach based on failure analysis"""
        if failure_analysis["recommendation"] == "fundamental_approach_change":
            return {
                "strategy": "completely_different_method",
                "description": "Use entirely different tool or approach",
                "changes": ["different_tool", "different_methodology", "simplified_scope"]
            }
        elif failure_analysis["recommendation"] == "simplify_or_parallelize":
            return {
                "strategy": "simplification",
                "description": "Break into smaller parts or use simpler approach",
                "changes": ["smaller_chunks", "simpler_commands", "sequential_instead_of_parallel"]
            }
        elif failure_analysis["recommendation"] == "alternative_sources":
            return {
                "strategy": "different_sources",
                "description": "Use different data sources or locations",
                "changes": ["alternative_locations", "different_search_terms", "backup_sources"]
            }
        else:
            return {
                "strategy": "tool_substitution",
                "description": "Use different tools with same objective",
                "changes": ["alternative_tools", "different_parameters", "modified_approach"]
            }
    
    def _create_execution_subtask(self, subtask_id: str, step: Dict[str, Any], is_first_step: bool) -> Dict[str, Any]:
        """Create an execution subtask from a detailed step"""
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
            "estimated_minutes": step.get("estimated_minutes", 3),
            "dependencies": [] if is_first_step else ["previous_step"],
            "specific_commands": step.get("specific_commands", []),
            "expected_output": step.get("expected_output", ""),
            "metadata": {
                "created_by_planning": True,
                "step_type": step["agent_type"],
                "planning_agent": self.name,
                "detailed_expansion": True
            }
        }
    
    def _create_alternative_subtask(self, alt_task_id: str, alternative: Dict[str, Any]) -> Dict[str, Any]:
        """Create alternative subtask for stuck task resolution"""
        return {
            "task_id": alt_task_id,
            "title": f"Alternative approach: {alternative['description']}",
            "description": alternative["description"],
            "created_by": self.name,
            "agent_type": "general",  # Will be refined by TaskBreakdownAgent if needed
            "status": "available",
            "progress": 0.0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "alternative_strategy": alternative["strategy"],
            "changes_from_original": alternative["changes"],
            "metadata": {
                "alternative_approach": True,
                "created_by_planning": True,
                "resolution_agent": self.name
            }
        }
    
    def _save_subtask_to_workspace(self, subtask: Dict[str, Any]):
        """Save subtask to workspace for other agents to find"""
        try:
            task_dir = self.current_tasks_dir / subtask["task_id"]
            task_dir.mkdir(parents=True, exist_ok=True)
            
            # Save task metadata
            task_file = task_dir / "task.json"
            with open(task_file, 'w') as f:
                json.dump(subtask, f, indent=2)
            
            # Create progress log
            progress_file = task_dir / "progress.log"
            with open(progress_file, 'w') as f:
                f.write(f"=== Planning Subtask Created: {datetime.now().isoformat()} ===\n")
                f.write(f"Task: {subtask['title']}\n")
                f.write(f"Type: {subtask['agent_type']}\n")
                f.write(f"Status: {subtask['status']}\n")
                f.write(f"Created by: {self.name} (Planning)\n")
                if subtask.get("specific_commands"):
                    f.write(f"Specific commands: {subtask['specific_commands']}\n")
                f.write(f"\n")
                
            print(f"📋 Created planning subtask: {subtask['task_id']}")
            
        except Exception as e:
            print(f"❌ Failed to save planning subtask {subtask['task_id']}: {e}")
    
    def _mark_planning_task_completed(self, task_id: str, detailed_steps: List[Dict[str, Any]]):
        """Mark the original planning task as completed"""
        try:
            task_dir = self.current_tasks_dir / task_id
            task_file = task_dir / "task.json"
            
            if task_file.exists():
                with open(task_file, 'r') as f:
                    task = json.load(f)
                
                task["status"] = "completed"
                task["completed_by"] = self.name
                task["completed_at"] = datetime.now().isoformat()
                task["planning_result"] = {
                    "detailed_steps_created": len(detailed_steps),
                    "expansion_completed": True
                }
                
                with open(task_file, 'w') as f:
                    json.dump(task, f, indent=2)
            
        except Exception as e:
            print(f"❌ Failed to mark planning task completed {task_id}: {e}")
    
    async def monitor_workspace(self):
        """Monitor workspace for tasks that need planning expansion"""
        print(f"🧠 {self.name} monitoring workspace for planning tasks...")
        
        while True:
            try:
                planning_tasks = self._find_planning_tasks()
                stuck_tasks = self._find_stuck_tasks()
                
                # Handle planning tasks first
                for task in planning_tasks:
                    print(f"📋 Found planning task: {task['task_id']}")
                    self._claim_task(task)
                    
                    # Expand the planning task
                    result = await self.expand_planning_task(
                        task['description'],
                        task['task_id'],
                        task.get('context', {})
                    )
                    
                    if result.get("success"):
                        print(f"✅ Completed planning expansion for {task['task_id']}")
                    else:
                        print(f"❌ Failed to expand planning for {task['task_id']}")
                
                # Handle stuck tasks
                for task in stuck_tasks:
                    print(f"🔄 Found stuck task: {task['task_id']}")
                    result = await self.resolve_stuck_task(
                        task['task_id'],
                        task.get('failure_context', {})
                    )
                    
                    if result.get("success"):
                        print(f"✅ Created alternative approach for {task['task_id']}")
                
                await asyncio.sleep(3)  # Check every 3 seconds
                
            except Exception as e:
                print(f"❌ Error in workspace monitoring: {e}")
                await asyncio.sleep(5)
    
    def _find_planning_tasks(self) -> List[Dict[str, Any]]:
        """Find tasks that need planning expansion"""
        planning_tasks = []
        
        try:
            if not self.current_tasks_dir.exists():
                return planning_tasks
                
            for task_dir in self.current_tasks_dir.iterdir():
                if not task_dir.is_dir():
                    continue
                    
                task_file = task_dir / "task.json"
                if not task_file.exists():
                    continue
                
                with open(task_file, 'r') as f:
                    task = json.load(f)
                
                # Look for tasks that need planning
                if (task.get("needs_planning", False) and
                    task.get("status") in ["available", "not_started"] and
                    not self._is_task_claimed(task)):
                    
                    planning_tasks.append(task)
            
        except Exception as e:
            print(f"❌ Error finding planning tasks: {e}")
        
        return planning_tasks
    
    def _find_stuck_tasks(self) -> List[Dict[str, Any]]:
        """Find tasks that appear to be stuck (failed multiple times)"""
        stuck_tasks = []
        
        try:
            if not self.current_tasks_dir.exists():
                return stuck_tasks
                
            for task_dir in self.current_tasks_dir.iterdir():
                if not task_dir.is_dir():
                    continue
                    
                task_file = task_dir / "task.json"
                if not task_file.exists():
                    continue
                
                with open(task_file, 'r') as f:
                    task = json.load(f)
                
                # Look for tasks that have failed multiple times or are marked as stuck
                if (task.get("status") == "failed" and
                    task.get("retry_count", 0) >= 2) or task.get("status") == "stuck":
                    
                    stuck_tasks.append(task)
                    
        except Exception as e:
            print(f"❌ Error finding stuck tasks: {e}")
        
        return stuck_tasks
    
    def _is_task_claimed(self, task: Dict[str, Any]) -> bool:
        """Check if task is already claimed by an agent"""
        return task.get("status") in ["claimed", "in_progress", "completed"]
    
    def _claim_task(self, task: Dict[str, Any]):
        """Claim a task by updating its status"""
        try:
            task["status"] = "claimed"
            task["claimed_by"] = self.name
            task["claimed_at"] = datetime.now().isoformat()
            
            task_dir = self.current_tasks_dir / task["task_id"]
            task_file = task_dir / "task.json"
            
            with open(task_file, 'w') as f:
                json.dump(task, f, indent=2)
            
        except Exception as e:
            print(f"❌ Failed to claim task {task['task_id']}: {e}")

# Create the agent instance
metacognition_agent = MetacognitionAgent()

if __name__ == "__main__":
    async def main():
        """Main entry point for the metacognition agent"""
        print("🧠 Starting Metacognition Agent - Task Expansion Specialist...")
        print("Specialization: Planning task expansion and stuck task resolution")
        print("Framework: Google ADK")
        print("Workspace monitoring: ENABLED")
        
        # Start monitoring workspace
        await metacognition_agent.monitor_workspace()
    
    asyncio.run(main()) 