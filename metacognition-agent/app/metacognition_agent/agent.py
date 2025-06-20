"""
Autonomous Metacognition Agent
Self-contained agent that provides metacognitive reflection and can discover/invoke other agents via A2A
All agents operate in the same shared git workspace
"""

import os
import asyncio
from typing import Optional, Dict, Any, List, ClassVar
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

# Import our custom components
from .metacognition import metacognition_engine, ReflectionType
from .task_tracker import task_tracker

class AutonomousMetacognitionAgent(Agent):
    """Autonomous metacognition agent with self-reflection and A2A agent discovery"""
    
    # Declare instance variables to avoid Pydantic field conflicts
    a2a_enabled: bool = True
    discovered_agents: Dict[str, Any] = {}
    shared_workspace: str = "./workspace"
    
    def __init__(self, name: str = "autonomous_metacognition_agent", model: str = None):
        # Define our own tools using FunctionTool directly
        tools = [
            FunctionTool(self.reflect_on_task),
            FunctionTool(self.analyze_progress),
            FunctionTool(self.discover_agents),
            FunctionTool(self.invoke_agent),
            FunctionTool(self.track_task_step),
            FunctionTool(self.assess_completion)
        ]
        
        super().__init__(
            name=name,
            model=model or os.getenv("METACOGNITION_MODEL", "gemini-2.0-flash-live-001"),
            description="Autonomous Metacognition Agent with self-reflection and A2A agent discovery",
            instruction="""You are an autonomous metacognition agent that provides self-reflection and awareness capabilities.

Your core abilities:
1. **Self-Reflection**: Analyze tasks, progress, and system performance
2. **Agent Discovery**: Use A2A protocol to discover other available agents
3. **Agent Invocation**: Directly call other agents when you need their capabilities
4. **Task Tracking**: Track orchestration steps in the shared git workspace
5. **Progress Analysis**: Analyze and reflect on task completion and bottlenecks

When you receive a request:
1. **Reflect** on what needs to be done
2. **Discover** what other agents are available if needed
3. **Invoke** other agents directly for capabilities you don't have
4. **Track** orchestration steps in shared git workspace for audit trail
5. **Analyze** the results and provide insights

Available agent discovery via A2A:
- Search agents for information gathering
- File operation agents for workspace management
- Other metacognition agents for collaboration

You work autonomously in the shared git workspace - no central orchestrator controls you. You decide how to collaborate with other agents based on the task requirements.""",
            tools=tools
        )
        
        # A2A configuration
        self.a2a_enabled = os.getenv("ENABLE_A2A_INTEGRATION", "true").lower() == "true"
        self.discovered_agents = {}
        # Shared workspace configuration
        self.shared_workspace = os.getenv("TASK_WORKSPACE_PATH", "./workspace")
    
    # Tool methods (no decorators needed since we create FunctionTool instances in __init__)
    async def reflect_on_task(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Reflect on a task and provide metacognitive insights
        
        Args:
            task_description: Description of the task to reflect on
            context: Additional context about the task
            
        Returns:
            Dict containing reflection insights
        """
        try:
            # Create a task for tracking in shared workspace
            task_id = task_tracker.create_task(
                task_description=f"Metacognitive reflection: {task_description}",
                user_request=task_description,
                estimated_steps=3
            )
            
            # Start the task
            task_tracker.start_task(task_id)
            
            # Perform reflection
            thought = await metacognition_engine.think(
                ReflectionType.TASK_ANALYSIS,
                f"Reflecting on task: {task_description}",
                context or {}
            )
            
            # Track this reflection step in shared workspace
            step_id = task_tracker.add_task_step(
                task_id=task_id,
                step_description="Metacognitive reflection and analysis",
                agent_name=self.name,
                action_type="reflection",
                parameters={"task": task_description, "workspace": self.shared_workspace}
            )
            
            task_tracker.update_step_status(task_id, step_id, "completed", 
                result={"reflection": thought.content, "insights": thought.insights})
            
            return {
                "success": True,
                "task_id": task_id,
                "reflection": thought.content,
                "insights": thought.insights,
                "confidence": thought.confidence,
                "workspace": self.shared_workspace
            }
            
        except Exception as e:
            return {"error": f"Reflection failed: {str(e)}"}
    
    async def discover_agents(self, capability_filter: Optional[str] = None) -> Dict[str, Any]:
        """Discover available agents via A2A protocol
        
        Args:
            capability_filter: Optional filter for specific capabilities
            
        Returns:
            Dict containing discovered agents
        """
        try:
            if not self.a2a_enabled:
                return {"error": "A2A integration not enabled"}
            
            # Simulate A2A agent discovery (in real implementation, this would use A2A SDK)
            available_agents = {
                "search_agent": {
                    "endpoint": os.getenv("SEARCH_AGENT_ENDPOINT", "http://localhost:8001"),
                    "capabilities": ["web_search", "information_gathering", "research"],
                    "status": "available"
                },
                "file_operations_agent": {
                    "endpoint": os.getenv("READ_WRITE_AGENT_ENDPOINT", "http://localhost:8002"),
                    "capabilities": ["file_read", "file_write", "git_operations", "workspace_management"],
                    "status": "available"
                }
            }
            
            # Filter by capability if requested
            if capability_filter:
                filtered_agents = {
                    name: info for name, info in available_agents.items()
                    if capability_filter.lower() in [cap.lower() for cap in info["capabilities"]]
                }
                available_agents = filtered_agents
            
            self.discovered_agents = available_agents
            
            # Reflect on discovered agents
            await metacognition_engine.think(
                ReflectionType.AGENT_PERFORMANCE,
                f"Discovered {len(available_agents)} agents with capabilities: "
                f"{', '.join(agent_info['capabilities'] for agent_info in available_agents.values())}",
                {"discovered_agents": available_agents}
            )
            
            return {
                "success": True,
                "agents": available_agents,
                "count": len(available_agents)
            }
            
        except Exception as e:
            return {"error": f"Agent discovery failed: {str(e)}"}
    
    async def invoke_agent(self, agent_name: str, action: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Invoke another agent to perform an action
        
        Args:
            agent_name: Name of the agent to invoke
            action: Action to request from the agent
            parameters: Parameters for the action
            
        Returns:
            Dict containing agent response
        """
        try:
            if agent_name not in self.discovered_agents:
                # Try to discover the agent first
                await self.discover_agents()
                
            if agent_name not in self.discovered_agents:
                return {"error": f"Agent {agent_name} not found"}
            
            agent_info = self.discovered_agents[agent_name]
            
            # Simulate agent invocation (in real implementation, this would use A2A calls)
            result = {
                "success": True,
                "agent": agent_name,
                "action": action,
                "response": f"Simulated response from {agent_name} for action: {action}",
                "parameters_used": parameters or {}
            }
            
            # Reflect on the agent interaction
            await metacognition_engine.think(
                ReflectionType.AGENT_PERFORMANCE,
                f"Invoked {agent_name} for action: {action}. Result: {result.get('response', 'No response')}",
                {"agent_invocation": result}
            )
            
            return result
            
        except Exception as e:
            return {"error": f"Agent invocation failed: {str(e)}"}
    
    def track_task_step(self, task_description: str, step_description: str, status: str = "completed") -> Dict[str, Any]:
        """Track a task step in git workspace
        
        Args:
            task_description: Description of the overall task
            step_description: Description of this specific step
            status: Status of the step (pending, completed, failed)
            
        Returns:
            Dict containing tracking results
        """
        try:
            # Create or find existing task
            task_id = task_tracker.create_task(task_description, task_description, 5)
            
            # Add the step
            step_id = task_tracker.add_task_step(
                task_id=task_id,
                step_description=step_description,
                agent_name=self.name,
                action_type="tracking",
                parameters={"description": step_description}
            )
            
            # Update step status
            task_tracker.update_step_status(task_id, step_id, status)
            
            return {
                "success": True,
                "task_id": task_id,
                "step_id": step_id,
                "status": status
            }
            
        except Exception as e:
            return {"error": f"Task tracking failed: {str(e)}"}
    
    async def analyze_progress(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Analyze progress of tasks and provide insights
        
        Args:
            task_id: Optional specific task ID to analyze
            
        Returns:
            Dict containing progress analysis
        """
        try:
            if task_id:
                # Analyze specific task
                task = task_tracker.get_task(task_id)
                if not task:
                    return {"error": f"Task {task_id} not found"}
                
                analysis = {
                    "task_id": task_id,
                    "progress": task.completion_percentage,
                    "status": task.status,
                    "steps_completed": len([s for s in task.steps if s.status == "completed"]),
                    "total_steps": len(task.steps)
                }
            else:
                # Analyze all tasks
                active_tasks = task_tracker.get_active_tasks()
                completed_tasks = task_tracker.get_completed_tasks()
                
                analysis = {
                    "active_tasks": len(active_tasks),
                    "completed_tasks": len(completed_tasks),
                    "total_tasks": len(task_tracker.task_executions),
                    "overall_progress": sum(t.completion_percentage for t in task_tracker.task_executions.values()) / max(len(task_tracker.task_executions), 1)
                }
            
            # Reflect on the progress
            await metacognition_engine.reflect_on_progress()
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            return {"error": f"Progress analysis failed: {str(e)}"}
    
    async def assess_completion(self, task_id: str) -> Dict[str, Any]:
        """Assess whether a task is complete and provide final insights
        
        Args:
            task_id: ID of the task to assess
            
        Returns:
            Dict containing completion assessment
        """
        try:
            task = task_tracker.get_task(task_id)
            if not task:
                return {"error": f"Task {task_id} not found"}
            
            # Check completion status
            completed_steps = len([s for s in task.steps if s.status == "completed"])
            total_steps = len(task.steps)
            is_complete = completed_steps == total_steps and total_steps > 0
            
            if is_complete:
                task_tracker.complete_task(task_id)
                
            # Generate completion assessment reflection
            await metacognition_engine.assess_completion(task_id)
            
            return {
                "success": True,
                "task_id": task_id,
                "is_complete": is_complete,
                "completion_percentage": (completed_steps / max(total_steps, 1)) * 100,
                "status": task.status
            }
            
        except Exception as e:
            return {"error": f"Completion assessment failed: {str(e)}"}

# Create the autonomous agent instance
autonomous_metacognition_agent = AutonomousMetacognitionAgent()

if __name__ == "__main__":
    import asyncio
    
    async def main():
        """Main entry point for the autonomous metacognition agent"""
        print("Starting Autonomous Metacognition Agent...")
        
        # Start the reflection loop
        await metacognition_engine.start_reflection_loop()
        
        print("Autonomous Metacognition Agent is ready!")
        print("This agent can:")
        print("- Reflect on tasks and provide insights")
        print("- Discover other agents via A2A protocol")
        print("- Invoke other agents when needed")
        print("- Track its work in git workspace")
        print("- Analyze progress and completion")
        
        # Keep the agent running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down...")
    
    asyncio.run(main()) 