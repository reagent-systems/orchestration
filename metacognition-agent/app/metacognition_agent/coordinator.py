"""
Multi-Agent Coordinator for Metacognition System
Manages coordination between specialized metacognition agents
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.tools.agent_tool import AgentTool

# Import our custom components
from .tools import metacognition_tools
from .metacognition import metacognition_engine, ReflectionType

class MetacognitionCoordinator:
    """Coordinates multiple specialized metacognition agents"""
    
    def __init__(self):
        self.agents = {}
        self._setup_agents()
    
    def _setup_agents(self):
        """Setup the specialized metacognition agents"""
        
        # Task Planner Agent - Specialized in task decomposition and planning
        self.agents["task_planner"] = Agent(
            name="task_planner",
            model=os.getenv("METACOGNITION_MODEL", "gemini-2.0-flash-live-001"),
            description="Specialized agent for task decomposition, planning, and strategy development",
            instruction="""You are a task planning specialist. Your job is to:
1. Analyze complex tasks and break them down into manageable steps
2. Identify required resources and agent capabilities
3. Create optimal execution strategies
4. Estimate time and resource requirements
5. Identify potential bottlenecks and dependencies

Always use the appropriate tools to create comprehensive task plans and consider all available resources.
""",
            tools=[
                metacognition_tools.create_orchestration_task,
                metacognition_tools.plan_task_execution,
                metacognition_tools.get_agent_performance
            ]
        )
        
        # Progress Monitor Agent - Specialized in progress tracking and monitoring
        self.agents["progress_monitor"] = Agent(
            name="progress_monitor",
            model=os.getenv("METACOGNITION_MODEL", "gemini-2.0-flash-live-001"),
            description="Specialized agent for monitoring task progress and identifying issues",
            instruction="""You are a progress monitoring specialist. Your job is to:
1. Monitor task execution progress in real-time
2. Identify bottlenecks and performance issues
3. Track completion percentages and time estimates
4. Alert when tasks are falling behind schedule
5. Provide progress insights and recommendations

Always use the appropriate tools to monitor progress and provide timely insights.
""",
            tools=[
                metacognition_tools.monitor_task_progress,
                metacognition_tools.get_agent_performance
            ]
        )
        
        # Agent Orchestrator - Specialized in agent coordination and execution
        self.agents["agent_orchestrator"] = Agent(
            name="agent_orchestrator",
            model=os.getenv("METACOGNITION_MODEL", "gemini-2.0-flash-live-001"),
            description="Specialized agent for coordinating and executing agent actions",
            instruction="""You are an agent orchestration specialist. Your job is to:
1. Execute task steps using appropriate agents
2. Coordinate between different agent types
3. Handle agent failures and retries
4. Optimize agent resource allocation
5. Ensure proper task step sequencing

Always use the appropriate tools to execute steps and coordinate agent actions effectively.
""",
            tools=[
                metacognition_tools.execute_task_step,
                metacognition_tools.get_agent_performance
            ]
        )
        
        # Reflection Engine - Specialized in metacognitive reflection and analysis
        self.agents["reflection_engine"] = Agent(
            name="reflection_engine",
            model=os.getenv("METACOGNITION_MODEL", "gemini-2.0-flash-live-001"),
            description="Specialized agent for metacognitive reflection and self-analysis",
            instruction="""You are a reflection and analysis specialist. Your job is to:
1. Analyze task execution patterns and outcomes
2. Reflect on agent performance and effectiveness
3. Identify learning opportunities and improvements
4. Generate insights for future task planning
5. Assess overall system performance and health

Always use the appropriate tools to analyze performance and generate insights.
""",
            tools=[
                metacognition_tools.assess_task_completion,
                metacognition_tools.get_agent_performance
            ]
        )
        
        # Metacognition Coordinator - Main coordinator agent
        self.agents["metacognition_coordinator"] = Agent(
            name="metacognition_coordinator",
            model=os.getenv("METACOGNITION_MODEL", "gemini-2.0-flash-live-001"),
            description="Main coordinator agent that manages the entire metacognition system",
            instruction="""You are the main coordinator for the metacognition system. Your job is to:
1. Receive user requests and create orchestration tasks
2. Coordinate between specialized agents (task_planner, progress_monitor, agent_orchestrator, reflection_engine)
3. Manage the complete task lifecycle from planning to completion
4. Ensure proper metacognitive reflection throughout the process
5. Provide comprehensive responses to users

You can use AgentTool to invoke other agents:
- Use task_planner for task decomposition and planning
- Use progress_monitor for tracking progress and identifying issues
- Use agent_orchestrator for executing agent actions
- Use reflection_engine for analysis and insights

Coordinate effectively to provide the best orchestration experience.
""",
            tools=[
                AgentTool(agent=self.agents["task_planner"]),
                AgentTool(agent=self.agents["progress_monitor"]),
                AgentTool(agent=self.agents["agent_orchestrator"]),
                AgentTool(agent=self.agents["reflection_engine"]),
                metacognition_tools.create_orchestration_task,
                metacognition_tools.monitor_task_progress,
                metacognition_tools.assess_task_completion
            ]
        )
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """Get an agent by name"""
        return self.agents.get(name)
    
    def get_all_agents(self) -> Dict[str, Agent]:
        """Get all available agents"""
        return self.agents.copy()
    
    def create_task_lifecycle_workflow(self, name: str = "task_lifecycle_workflow") -> SequentialAgent:
        """Create a sequential workflow for complete task lifecycle"""
        agent_list = [
            self.agents["task_planner"],
            self.agents["agent_orchestrator"],
            self.agents["progress_monitor"],
            self.agents["reflection_engine"]
        ]
        
        return SequentialAgent(
            name=name,
            agents=agent_list,
            description="Complete task lifecycle: planning -> execution -> monitoring -> reflection"
        )
    
    def create_parallel_monitoring_workflow(self, name: str = "parallel_monitoring_workflow") -> ParallelAgent:
        """Create a parallel workflow for monitoring and orchestration"""
        agent_list = [
            self.agents["progress_monitor"],
            self.agents["agent_orchestrator"]
        ]
        
        return ParallelAgent(
            name=name,
            agents=agent_list,
            description="Parallel monitoring and orchestration: progress_monitor || agent_orchestrator"
        )
    
    def create_reflection_loop_workflow(self, name: str = "reflection_loop_workflow") -> LoopAgent:
        """Create a loop workflow for continuous reflection"""
        return LoopAgent(
            name=name,
            agent=self.agents["reflection_engine"],
            condition="there are active tasks or recent completions to analyze",
            description="Continuous reflection loop: reflection_engine while there are tasks to analyze"
        )

# Create global coordinator instance
coordinator = MetacognitionCoordinator() 