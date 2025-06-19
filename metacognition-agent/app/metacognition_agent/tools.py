"""
Metacognition Tools for Orchestration
Provides tools for task planning, agent orchestration, progress monitoring, reflection, and git-based tracking
"""

import os
import asyncio
import json
import aiohttp
from typing import Dict, List, Optional, Any, Tuple
from google.adk.tools import FunctionTool
# from google.adk.annotations import Schema  # <-- Removed, not available in ADK 1.3.0

# Import our custom components
from .metacognition import metacognition_engine, ReflectionType
from .task_tracker import task_tracker

class MetacognitionTools:
    """Collection of tools for the metacognition agent"""
    
    def __init__(self):
        self.available_agents = {
            "search_agent": {
                "endpoint": os.getenv("SEARCH_AGENT_ENDPOINT", "http://localhost:8001/search_agent"),
                "capabilities": ["web_search", "information_gathering", "research"],
                "description": "Web search and information gathering agent"
            },
            "read_write_agent": {
                "endpoint": os.getenv("READ_WRITE_AGENT_ENDPOINT", "http://localhost:8002/file_operations_agent"),
                "capabilities": ["file_operations", "git_management", "workspace_management"],
                "description": "File operations and workspace management agent"
            }
        }
        self.agent_performance = {}
    
    @FunctionTool
    def create_orchestration_task(
        self,
        task_description: str,
        user_request: str,
        estimated_steps: int = 10
    ) -> Dict[str, Any]:
        """Create a new orchestration task with git-based tracking
        
        Args:
            task_description: Description of the task to be orchestrated
            user_request: Original user request
            estimated_steps: Estimated number of steps needed (default: 10)
            
        Returns:
            Dict containing task creation results
        """
        try:
            # Create task in tracker
            task_id = task_tracker.create_task(task_description, user_request, estimated_steps)
            
            # Update metacognition engine
            metacognition_engine.update_task_progress(
                task_id=task_id,
                current_step=0,
                total_steps=estimated_steps,
                status="pending",
                completion_percentage=0.0
            )
            
            # Generate initial reflection
            asyncio.create_task(metacognition_engine.think(
                ReflectionType.TASK_ANALYSIS,
                f"Created new orchestration task: {task_description}\n"
                f"Task ID: {task_id}\n"
                f"Estimated steps: {estimated_steps}\n"
                f"User request: {user_request}",
                {"task_id": task_id, "task_description": task_description}
            ))
            
            return {
                "success": True,
                "task_id": task_id,
                "task_description": task_description,
                "status": "pending",
                "estimated_steps": estimated_steps
            }
        except Exception as e:
            return {"error": f"Failed to create task: {str(e)}"}
    
    @FunctionTool
    def plan_task_execution(
        self,
        task_id: str,
        task_description: str,
        available_resources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Plan the execution steps for a given task
        
        Args:
            task_id: ID of the task to plan
            task_description: Description of the task
            available_resources: List of available agents and resources
            
        Returns:
            Dict containing execution plan
        """
        try:
            if task_id not in task_tracker.task_executions:
                return {"error": f"Task {task_id} not found"}
            
            # Start the task
            task_tracker.start_task(task_id)
            
            # Analyze task and create execution plan
            plan = self._create_execution_plan(task_description, available_resources or list(self.available_agents.keys()))
            
            # Add planned steps to task tracker
            for i, step in enumerate(plan["steps"], 1):
                step_id = task_tracker.add_task_step(
                    task_id=task_id,
                    step_description=step["description"],
                    agent_name=step["agent"],
                    action_type=step["action_type"],
                    parameters=step.get("parameters", {})
                )
                step["step_id"] = step_id
            
            # Update metacognition
            metacognition_engine.update_task_progress(
                task_id=task_id,
                current_step=0,
                total_steps=len(plan["steps"]),
                status="planning",
                completion_percentage=0.0
            )
            
            # Reflect on the plan
            asyncio.create_task(metacognition_engine.think(
                ReflectionType.STRATEGY_REFLECTION,
                f"Created execution plan for task {task_id}:\n"
                f"Total steps: {len(plan['steps'])}\n"
                f"Estimated duration: {plan['estimated_duration']}\n"
                f"Required agents: {', '.join(plan['required_agents'])}",
                {"task_id": task_id, "plan": plan}
            ))
            
            return {
                "success": True,
                "task_id": task_id,
                "plan": plan,
                "total_steps": len(plan["steps"])
            }
        except Exception as e:
            return {"error": f"Failed to plan task: {str(e)}"}
    
    @FunctionTool
    async def execute_task_step(
        self,
        task_id: str,
        step_id: str
    ) -> Dict[str, Any]:
        """Execute a specific step in a task
        
        Args:
            task_id: ID of the task
            step_id: ID of the step to execute
            
        Returns:
            Dict containing execution results
        """
        try:
            task = task_tracker.get_task(task_id)
            if not task:
                return {"error": f"Task {task_id} not found"}
            
            step = next((s for s in task.steps if s.step_id == step_id), None)
            if not step:
                return {"error": f"Step {step_id} not found"}
            
            # Update step status to in_progress
            task_tracker.update_step_status(task_id, step_id, "in_progress")
            
            # Execute the step
            result = await self._execute_agent_action(
                agent_name=step.agent_name,
                action_type=step.action_type,
                parameters=step.parameters
            )
            
            # Update step with result
            status = "completed" if result.get("success") else "failed"
            task_tracker.update_step_status(
                task_id, step_id, status, 
                result=result,
                metadata={"execution_time": result.get("duration", 0)}
            )
            
            # Update metacognition
            metacognition_engine.update_task_progress(
                task_id=task_id,
                current_step=step.step_number,
                total_steps=len(task.steps),
                status="executing",
                completion_percentage=(step.step_number / len(task.steps)) * 100,
                successes=[step.step_description] if status == "completed" else [],
                failures=[step.step_description] if status == "failed" else []
            )
            
            # Reflect on step execution
            asyncio.create_task(metacognition_engine.think(
                ReflectionType.AGENT_PERFORMANCE,
                f"Executed step {step.step_number} for task {task_id}:\n"
                f"Agent: {step.agent_name}\n"
                f"Action: {step.action_type}\n"
                f"Status: {status}\n"
                f"Result: {result.get('message', 'No message')}",
                {"task_id": task_id, "step_id": step_id, "result": result}
            ))
            
            return {
                "success": True,
                "task_id": task_id,
                "step_id": step_id,
                "status": status,
                "result": result
            }
        except Exception as e:
            return {"error": f"Failed to execute step: {str(e)}"}
    
    @FunctionTool
    def monitor_task_progress(
        self,
        task_id: str
    ) -> Dict[str, Any]:
        """Monitor the progress of a task and provide insights
        
        Args:
            task_id: ID of the task to monitor
            
        Returns:
            Dict containing progress report
        """
        try:
            task = task_tracker.get_task(task_id)
            if not task:
                return {"error": f"Task {task_id} not found"}
            
            # Calculate progress metrics
            completed_steps = len([s for s in task.steps if s.status == "completed"])
            failed_steps = len([s for s in task.steps if s.status == "failed"])
            pending_steps = len([s for s in task.steps if s.status == "pending"])
            
            progress_percentage = (completed_steps / len(task.steps)) * 100 if task.steps else 0
            
            # Identify bottlenecks
            bottlenecks = []
            for step in task.steps:
                if step.status == "failed":
                    bottlenecks.append(f"Step {step.step_number}: {step.step_description}")
                elif step.duration and step.duration > 30:  # Steps taking more than 30 seconds
                    bottlenecks.append(f"Step {step.step_number}: Slow execution ({step.duration:.1f}s)")
            
            # Generate progress report
            progress_report = {
                "task_id": task_id,
                "task_description": task.task_description,
                "status": task.status,
                "progress_percentage": progress_percentage,
                "completed_steps": completed_steps,
                "failed_steps": failed_steps,
                "pending_steps": pending_steps,
                "total_steps": len(task.steps),
                "bottlenecks": bottlenecks,
                "estimated_completion": task.estimated_completion,
                "git_commits": len(task.git_commits)
            }
            
            # Update metacognition
            metacognition_engine.update_task_progress(
                task_id=task_id,
                current_step=completed_steps,
                total_steps=len(task.steps),
                status=task.status,
                completion_percentage=progress_percentage,
                bottlenecks=bottlenecks
            )
            
            # Reflect on progress
            asyncio.create_task(metacognition_engine.reflect_on_task(task_id, task.task_description))
            
            return {
                "success": True,
                "progress_report": progress_report
            }
        except Exception as e:
            return {"error": f"Failed to monitor progress: {str(e)}"}
    
    @FunctionTool
    def assess_task_completion(
        self,
        task_id: str
    ) -> Dict[str, Any]:
        """Assess whether a task is complete and provide final evaluation
        
        Args:
            task_id: ID of the task to assess
            
        Returns:
            Dict containing completion assessment
        """
        try:
            task = task_tracker.get_task(task_id)
            if not task:
                return {"error": f"Task {task_id} not found"}
            
            # Check if all steps are completed
            all_completed = all(s.status == "completed" for s in task.steps)
            
            if all_completed:
                # Mark task as completed
                task_tracker.complete_task(task_id, {
                    "completion_assessment": "All steps completed successfully",
                    "total_duration": (task.completed_at - task.started_at).total_seconds() if task.completed_at and task.started_at else 0
                })
                
                # Final reflection
                asyncio.create_task(metacognition_engine.assess_completion(task_id))
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "status": "completed",
                    "completion_percentage": 100.0,
                    "message": "Task completed successfully"
                }
            else:
                # Check for failed steps
                failed_steps = [s for s in task.steps if s.status == "failed"]
                if failed_steps:
                    task_tracker.fail_task(task_id, f"Task failed due to {len(failed_steps)} failed steps")
                    return {
                        "success": False,
                        "task_id": task_id,
                        "status": "failed",
                        "failed_steps": len(failed_steps),
                        "message": f"Task failed due to {len(failed_steps)} failed steps"
                    }
                else:
                    return {
                        "success": False,
                        "task_id": task_id,
                        "status": "in_progress",
                        "message": "Task is still in progress"
                    }
        except Exception as e:
            return {"error": f"Failed to assess completion: {str(e)}"}
    
    @FunctionTool
    def get_agent_performance(self) -> Dict[str, Any]:
        """Get performance metrics for all agents
        
        Returns:
            Dict containing agent performance data
        """
        try:
            performance_data = {}
            
            for agent_name, agent_info in self.available_agents.items():
                if agent_name in self.agent_performance:
                    performance_data[agent_name] = self.agent_performance[agent_name]
                else:
                    performance_data[agent_name] = {
                        "endpoint": agent_info["endpoint"],
                        "capabilities": agent_info["capabilities"],
                        "total_tasks": 0,
                        "success_rate": 0.0,
                        "avg_response_time": 0.0,
                        "last_used": None
                    }
            
            return {
                "success": True,
                "agent_performance": performance_data
            }
        except Exception as e:
            return {"error": f"Failed to get agent performance: {str(e)}"}
    
    def _create_execution_plan(self, task_description: str, available_agents: List[str]) -> Dict[str, Any]:
        """Create an execution plan for a task"""
        # This is a simplified planner - in practice, this would use LLM reasoning
        steps = []
        
        # Analyze task and determine required steps
        if "search" in task_description.lower() or "find" in task_description.lower():
            steps.append({
                "description": "Gather information using search agent",
                "agent": "search_agent",
                "action_type": "web_search",
                "parameters": {"query": task_description}
            })
        
        if "file" in task_description.lower() or "write" in task_description.lower() or "create" in task_description.lower():
            steps.append({
                "description": "Perform file operations using read-write agent",
                "agent": "read_write_agent",
                "action_type": "file_operations",
                "parameters": {"operation": "analyze_and_execute", "task": task_description}
            })
        
        # Add planning and analysis steps
        steps.insert(0, {
            "description": "Analyze task requirements and create detailed plan",
            "agent": "metacognition_agent",
            "action_type": "task_analysis",
            "parameters": {"task_description": task_description}
        })
        
        steps.append({
            "description": "Finalize task and provide comprehensive report",
            "agent": "metacognition_agent",
            "action_type": "task_completion",
            "parameters": {"task_description": task_description}
        })
        
        return {
            "steps": steps,
            "estimated_duration": len(steps) * 30,  # 30 seconds per step
            "required_agents": list(set(step["agent"] for step in steps)),
            "complexity": "medium" if len(steps) > 5 else "low"
        }
    
    async def _execute_agent_action(self, agent_name: str, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action using a specific agent"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            if agent_name not in self.available_agents:
                return {
                    "success": False,
                    "error": f"Agent {agent_name} not available",
                    "duration": 0
                }
            
            agent_info = self.available_agents[agent_name]
            
            # In a real implementation, this would make HTTP calls to agent endpoints
            # For now, we'll simulate the execution
            await asyncio.sleep(1)  # Simulate execution time
            
            # Simulate different agent responses
            if agent_name == "search_agent":
                result = {
                    "success": True,
                    "message": f"Search completed for: {parameters.get('query', 'unknown')}",
                    "results": ["Result 1", "Result 2", "Result 3"],
                    "duration": asyncio.get_event_loop().time() - start_time
                }
            elif agent_name == "read_write_agent":
                result = {
                    "success": True,
                    "message": f"File operations completed for: {action_type}",
                    "files_processed": 3,
                    "duration": asyncio.get_event_loop().time() - start_time
                }
            else:
                result = {
                    "success": True,
                    "message": f"Action {action_type} completed successfully",
                    "duration": asyncio.get_event_loop().time() - start_time
                }
            
            # Update agent performance
            self._update_agent_performance(agent_name, result)
            
            return result
            
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            return {
                "success": False,
                "error": str(e),
                "duration": duration
            }
    
    def _update_agent_performance(self, agent_name: str, result: Dict[str, Any]):
        """Update agent performance metrics"""
        if agent_name not in self.agent_performance:
            self.agent_performance[agent_name] = {
                "total_tasks": 0,
                "successful_tasks": 0,
                "failed_tasks": 0,
                "total_response_time": 0.0,
                "last_used": None
            }
        
        perf = self.agent_performance[agent_name]
        perf["total_tasks"] += 1
        perf["last_used"] = asyncio.get_event_loop().time()
        
        if result.get("success"):
            perf["successful_tasks"] += 1
        else:
            perf["failed_tasks"] += 1
        
        perf["total_response_time"] += result.get("duration", 0)
        perf["success_rate"] = perf["successful_tasks"] / perf["total_tasks"]
        perf["avg_response_time"] = perf["total_response_time"] / perf["total_tasks"]

# Create global tools instance
metacognition_tools = MetacognitionTools() 