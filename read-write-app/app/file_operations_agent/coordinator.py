"""
Multi-Agent Coordinator for File Operations
Manages coordination between different specialized agents for file operations
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.tools import AgentTool
from .tools import file_tools

class FileOperationsCoordinator:
    """Coordinates multiple agents for file operations"""
    
    def __init__(self):
        self.agents = {}
        self.a2a_agents = {}
        self._setup_agents()
    
    def _setup_agents(self):
        """Setup the specialized agents"""
        
        # File Reader Agent - Specialized in reading and analyzing files
        self.agents["file_reader"] = Agent(
            name="file_reader",
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-live-001"),
            description="Specialized agent for reading and analyzing files in the workspace",
            instruction="""You are a file reading specialist. Your job is to:
1. Read files from the workspace using the provided tools
2. Analyze file content and structure
3. Provide insights about file content
4. Identify file types and formats
5. Extract key information from files

Always use the appropriate tools to read files and provide clear, structured analysis.
""",
            tools=[
                file_tools.read_file,
                file_tools.list_files,
                file_tools.git_status
            ]
        )
        
        # File Writer Agent - Specialized in writing and creating files
        self.agents["file_writer"] = Agent(
            name="file_writer",
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-live-001"),
            description="Specialized agent for writing and creating files in the workspace",
            instruction="""You are a file writing specialist. Your job is to:
1. Write content to files in the workspace
2. Create new files with appropriate content
3. Modify existing files when needed
4. Ensure proper file formatting and structure
5. Create directories when needed

Always use the appropriate tools to write files and ensure content is well-structured.
""",
            tools=[
                file_tools.write_file,
                file_tools.create_directory,
                file_tools.list_files,
                file_tools.git_commit
            ]
        )
        
        # Git Manager Agent - Specialized in git operations
        self.agents["git_manager"] = Agent(
            name="git_manager",
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-live-001"),
            description="Specialized agent for managing git operations in the workspace",
            instruction="""You are a git management specialist. Your job is to:
1. Monitor git status of the workspace
2. Commit changes when appropriate
3. Manage git operations and history
4. Provide git status information
5. Ensure proper git workflow

Always use the appropriate tools to manage git operations and maintain clean history.
""",
            tools=[
                file_tools.git_status,
                file_tools.git_commit,
                file_tools.list_files
            ]
        )
        
        # File Operations Coordinator - Main coordinator agent
        self.agents["file_coordinator"] = Agent(
            name="file_coordinator",
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-live-001"),
            description="Main coordinator agent that manages file operations workflow",
            instruction="""You are the main coordinator for file operations. Your job is to:
1. Analyze user requests and determine the appropriate workflow
2. Coordinate between specialized agents (file_reader, file_writer, git_manager)
3. Delegate tasks to the appropriate specialized agents
4. Ensure proper workflow execution
5. Provide comprehensive responses to users

You can use AgentTool to invoke other agents:
- Use file_reader for reading and analyzing files
- Use file_writer for writing and creating files  
- Use git_manager for git operations

Coordinate effectively to provide the best user experience.
""",
            tools=[
                AgentTool(agent=self.agents["file_reader"]),
                AgentTool(agent=self.agents["file_writer"]),
                AgentTool(agent=self.agents["git_manager"]),
                file_tools.list_files,
                file_tools.git_status
            ]
        )
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """Get an agent by name"""
        return self.agents.get(name)
    
    def get_all_agents(self) -> Dict[str, Agent]:
        """Get all available agents"""
        return self.agents.copy()
    
    def create_sequential_workflow(self, agents: List[str], name: str = "sequential_workflow") -> SequentialAgent:
        """Create a sequential workflow with specified agents"""
        agent_list = [self.agents[agent] for agent in agents if agent in self.agents]
        
        return SequentialAgent(
            name=name,
            agents=agent_list,
            description=f"Sequential workflow: {' -> '.join(agents)}"
        )
    
    def create_parallel_workflow(self, agents: List[str], name: str = "parallel_workflow") -> ParallelAgent:
        """Create a parallel workflow with specified agents"""
        agent_list = [self.agents[agent] for agent in agents if agent in self.agents]
        
        return ParallelAgent(
            name=name,
            agents=agent_list,
            description=f"Parallel workflow: {' || '.join(agents)}"
        )
    
    def create_loop_workflow(self, agent: str, condition: str, name: str = "loop_workflow") -> LoopAgent:
        """Create a loop workflow with a specified agent"""
        if agent not in self.agents:
            raise ValueError(f"Agent {agent} not found")
        
        return LoopAgent(
            name=name,
            agent=self.agents[agent],
            condition=condition,
            description=f"Loop workflow: {agent} while {condition}"
        )

# Create global coordinator instance
coordinator = FileOperationsCoordinator() 