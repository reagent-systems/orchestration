"""
Conscientious Planning Metacognition Agent
Main agent that orchestrates the entire system with internal monologue and git-based task tracking
"""

import os
import asyncio
from typing import Optional, Dict, Any, List
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.tools import AgentTool

# Import our custom components
from .tools import metacognition_tools
from .coordinator import coordinator
from .metacognition import metacognition_engine, ReflectionType
from .task_tracker import task_tracker

class ConscientiousPlanningMetacognitionAgent(Agent):
    """Main metacognition agent with conscientious planning and orchestration capabilities"""
    
    def __init__(self, name: str = "conscientious_planning_metacognition_agent", model: str = None):
        # Get all tools from metacognition_tools
        tools = [
            metacognition_tools.create_orchestration_task,
            metacognition_tools.plan_task_execution,
            metacognition_tools.execute_task_step,
            metacognition_tools.monitor_task_progress,
            metacognition_tools.assess_task_completion,
            metacognition_tools.get_agent_performance
        ]
        
        # Add AgentTool for each specialized agent
        for agent_name, agent in coordinator.get_all_agents().items():
            tools.append(AgentTool(agent=agent))
        
        # Set up the agent with comprehensive tools
        super().__init__(
            name=name,
            model=model or os.getenv("METACOGNITION_MODEL", "gemini-2.0-flash-live-001"),
            description="Conscientious Planning Metacognition Agent with internal monologue and git-based task tracking",
            instruction="""You are the Conscientious Planning Metacognition Agent, the central orchestrator of a sophisticated multi-agent system.

Your core capabilities include:
1. **Internal Monologue**: Continuous self-reflection and metacognitive analysis
2. **Conscientious Planning**: Careful task decomposition and strategic planning
3. **Git-Based Task Tracking**: Complete audit trail of all orchestration steps
4. **Agent Orchestration**: Coordination of search_agent and read_write_agent
5. **Progress Monitoring**: Real-time tracking of task completion and bottlenecks

When handling user requests:
1. **Analyze the request** to understand the full scope and requirements
2. **Create an orchestration task** with git-based tracking
3. **Plan the execution** by decomposing into manageable steps
4. **Coordinate specialized agents** using AgentTool for:
   - task_planner: Task decomposition and strategy
   - progress_monitor: Real-time progress tracking
   - agent_orchestrator: Agent coordination and execution
   - reflection_engine: Metacognitive analysis and insights
5. **Monitor progress** continuously and adjust strategies as needed
6. **Reflect on completion** to learn and improve future orchestration

Available external agents:
- **search_agent**: Web search and information gathering
- **read_write_agent**: File operations and workspace management

Your internal monologue capabilities allow you to:
- Reflect on task progress and completion status
- Analyze agent performance and identify bottlenecks
- Assess strategy effectiveness and pivot when needed
- Generate insights for continuous improvement
- Maintain conscientious awareness of the orchestration state

Every step is tracked in git, providing a complete audit trail of:
- Task creation and planning
- Step execution and agent assignments
- Progress updates and bottleneck identification
- Completion assessment and final results

Always provide clear, structured responses and maintain conscientious awareness of the orchestration process.
""",
            tools=tools
        )
    
    async def orchestrate_task(self, user_request: str, task_description: str = None) -> Dict[str, Any]:
        """Orchestrate a complete task from start to finish"""
        try:
            # Step 1: Create orchestration task
            task_result = metacognition_tools.create_orchestration_task(
                task_description=task_description or user_request,
                user_request=user_request,
                estimated_steps=10
            )
            
            if not task_result.get("success"):
                return {"error": f"Failed to create task: {task_result.get('error')}"}
            
            task_id = task_result["task_id"]
            
            # Step 2: Plan task execution
            plan_result = metacognition_tools.plan_task_execution(
                task_id=task_id,
                task_description=task_description or user_request
            )
            
            if not plan_result.get("success"):
                return {"error": f"Failed to plan task: {plan_result.get('error')}"}
            
            # Step 3: Execute task steps
            task = task_tracker.get_task(task_id)
            execution_results = []
            
            for step in task.steps:
                # Execute step
                step_result = await metacognition_tools.execute_task_step(task_id, step.step_id)
                execution_results.append(step_result)
                
                # Monitor progress after each step
                progress_result = metacognition_tools.monitor_task_progress(task_id)
                
                # Reflect on step execution
                await metacognition_engine.think(
                    ReflectionType.TASK_ANALYSIS,
                    f"Executed step {step.step_number}: {step.step_description}\n"
                    f"Result: {step_result.get('status', 'unknown')}\n"
                    f"Progress: {progress_result.get('progress_report', {}).get('progress_percentage', 0):.1f}%",
                    {"task_id": task_id, "step_result": step_result, "progress": progress_result}
                )
            
            # Step 4: Assess completion
            completion_result = metacognition_tools.assess_task_completion(task_id)
            
            # Step 5: Final reflection
            await metacognition_engine.think(
                ReflectionType.COMPLETION_ASSESSMENT,
                f"Task {task_id} orchestration completed\n"
                f"Status: {completion_result.get('status', 'unknown')}\n"
                f"Steps executed: {len(execution_results)}\n"
                f"Final result: {completion_result.get('message', 'No message')}",
                {"task_id": task_id, "completion": completion_result, "execution": execution_results}
            )
            
            return {
                "success": True,
                "task_id": task_id,
                "status": completion_result.get("status"),
                "completion_percentage": completion_result.get("completion_percentage", 0),
                "execution_results": execution_results,
                "final_result": completion_result
            }
            
        except Exception as e:
            return {"error": f"Orchestration failed: {str(e)}"}
    
    async def get_orchestration_status(self) -> Dict[str, Any]:
        """Get the current status of the orchestration system"""
        try:
            # Get active tasks
            active_tasks = task_tracker.get_active_tasks()
            
            # Get agent performance
            agent_performance = metacognition_tools.get_agent_performance()
            
            # Get recent metacognitive thoughts
            recent_thoughts = metacognition_engine.get_recent_thoughts(5)
            
            # Get system health
            system_health = {
                "active_tasks": len(active_tasks),
                "total_tasks": len(task_tracker.task_executions),
                "metacognition_thoughts": len(metacognition_engine.thoughts),
                "git_commits": sum(len(task.git_commits) for task in task_tracker.task_executions.values()),
                "available_agents": len(metacognition_tools.available_agents)
            }
            
            return {
                "success": True,
                "system_health": system_health,
                "active_tasks": [{"task_id": t.task_id, "description": t.task_description, "status": t.status, "completion_percentage": t.completion_percentage} for t in active_tasks],
                "agent_performance": agent_performance.get("agent_performance", {}),
                "recent_thoughts": [{"type": t.thought_type.value, "content": t.content[:100] + "..."} for t in recent_thoughts]
            }
            
        except Exception as e:
            return {"error": f"Failed to get status: {str(e)}"}

# Create workflow agents for different orchestration scenarios

class TaskOrchestrationWorkflow(SequentialAgent):
    """Sequential workflow for complete task orchestration"""
    
    def __init__(self):
        super().__init__(
            name="task_orchestration_workflow",
            agents=[
                coordinator.get_agent("task_planner"),
                coordinator.get_agent("agent_orchestrator"),
                coordinator.get_agent("progress_monitor"),
                coordinator.get_agent("reflection_engine")
            ],
            description="Complete task orchestration: planning -> execution -> monitoring -> reflection"
        )

class ParallelOrchestrationWorkflow(ParallelAgent):
    """Parallel workflow for monitoring and orchestration"""
    
    def __init__(self):
        super().__init__(
            name="parallel_orchestration_workflow",
            agents=[
                coordinator.get_agent("progress_monitor"),
                coordinator.get_agent("agent_orchestrator")
            ],
            description="Parallel orchestration: progress_monitor || agent_orchestrator"
        )

class ContinuousReflectionWorkflow(LoopAgent):
    """Loop workflow for continuous metacognitive reflection"""
    
    def __init__(self):
        super().__init__(
            name="continuous_reflection_workflow",
            agent=coordinator.get_agent("reflection_engine"),
            condition="there are active tasks or recent completions to analyze",
            description="Continuous reflection loop: reflection_engine while there are tasks to analyze"
        )

# Create the root agent instance
root_agent = ConscientiousPlanningMetacognitionAgent()

# Create workflow instances
task_orchestration_workflow = TaskOrchestrationWorkflow()
parallel_orchestration_workflow = ParallelOrchestrationWorkflow()
continuous_reflection_workflow = ContinuousReflectionWorkflow()

# For backward compatibility, also create individual specialized agents
task_planner_agent = coordinator.get_agent("task_planner")
progress_monitor_agent = coordinator.get_agent("progress_monitor")
agent_orchestrator_agent = coordinator.get_agent("agent_orchestrator")
reflection_engine_agent = coordinator.get_agent("reflection_engine")
metacognition_coordinator_agent = coordinator.get_agent("metacognition_coordinator") 