"""
File Operations Agent System
Combines LLM agents, workflow agents, and A2A integration for file operations
"""

import os
import asyncio
from typing import Optional, Dict, Any, List
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.tools import AgentTool

# Import our custom components
from .tools import file_tools
from .coordinator import coordinator

# A2A Integration imports (when A2A SDK is available)
try:
    from a2a_sdk import A2AClient, AgentCard
    A2A_AVAILABLE = True
except ImportError:
    A2A_AVAILABLE = False
    print("A2A SDK not available. A2A features will be disabled.")

class A2AIntegrationLayer:
    """A2A integration layer for external agent communication"""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.agent_registry = {}
        self.a2a_client = None
        self.enabled = False
        
        if A2A_AVAILABLE:
            self.a2a_client = A2AClient()
            self.enabled = True
            print("A2A integration layer initialized for file operations")
        else:
            print("A2A integration layer disabled - SDK not available")
    
    async def discover_external_agents(self):
        """Discover external agents via A2A protocol"""
        if not self.enabled or not self.a2a_client:
            return []
        
        try:
            # Discover agents from A2A registry
            agents = await self.a2a_client.discover_agents()
            for agent in agents:
                self.agent_registry[agent.name] = agent
            print(f"Discovered {len(agents)} external A2A agents for file operations")
            return agents
        except Exception as e:
            print(f"Error discovering A2A agents: {e}")
            return []
    
    async def delegate_task(self, agent_name: str, task: str, context: Dict[str, Any] = None):
        """Delegate task to external A2A agent"""
        if not self.enabled or not self.a2a_client:
            return None
        
        if agent_name not in self.agent_registry:
            print(f"A2A Agent {agent_name} not found in registry")
            return None
        
        agent = self.agent_registry[agent_name]
        try:
            result = await self.a2a_client.execute_task(
                agent.endpoint,
                task=task,
                context=context or {},
                capabilities=agent.capabilities
            )
            return result
        except Exception as e:
            print(f"Error delegating task to A2A agent {agent_name}: {e}")
            return None

class EnhancedFileOperationsAgent(Agent):
    """Enhanced file operations agent with A2A integration capabilities"""
    
    def __init__(self, name: str = "enhanced_file_operations_agent", model: str = None):
        # Initialize A2A integration layer
        self.a2a_layer = A2AIntegrationLayer(
            host=os.getenv("A2A_HOST", "localhost"),
            port=int(os.getenv("A2A_PORT", "8080"))
        )
        
        # Get all tools from file_tools
        tools = [
            file_tools.read_file,
            file_tools.write_file,
            file_tools.list_files,
            file_tools.delete_file,
            file_tools.create_directory,
            file_tools.git_status,
            file_tools.git_commit
        ]
        
        # Add AgentTool for each specialized agent
        for agent_name, agent in coordinator.get_all_agents().items():
            tools.append(AgentTool(agent=agent))
        
        # Set up the agent with comprehensive tools
        super().__init__(
            name=name,
            model=model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash-live-001"),
            description="Enhanced agent for file operations with git integration and external agent coordination.",
            instruction="""You are an expert file operations agent with access to a git workspace and external specialized agents.

Your capabilities include:
1. **File Operations**: Read, write, delete, and list files in the workspace
2. **Git Integration**: Monitor git status, commit changes, and manage version control
3. **Multi-Agent Coordination**: Delegate tasks to specialized agents (file_reader, file_writer, git_manager)
4. **External Agent Integration**: Connect to external A2A agents for additional capabilities

When handling requests:
1. **Analyze the request** to determine the best approach
2. **Use appropriate tools** for file operations
3. **Coordinate with specialized agents** when needed using AgentTool
4. **Consider external A2A agents** for specialized tasks not covered locally
5. **Maintain git workflow** by committing changes appropriately

Specialized agents available:
- **file_reader**: For reading and analyzing files
- **file_writer**: For writing and creating files
- **git_manager**: For git operations and version control

Always provide clear, structured responses and ensure proper file and git management.
""",
            tools=tools
        )
        
        # Initialize A2A discovery if enabled
        if os.getenv("ENABLE_A2A_INTEGRATION", "true").lower() == "true":
            asyncio.create_task(self._initialize_a2a())
    
    async def _initialize_a2a(self):
        """Initialize A2A agent discovery"""
        if self.a2a_layer.enabled:
            await self.a2a_layer.discover_external_agents()
    
    async def execute_with_a2a_fallback(self, task: str, context: Dict[str, Any] = None):
        """Execute task with A2A agent fallback if needed"""
        # First try with local capabilities
        try:
            result = await self.execute(task, context)
            return {
                "source": "local",
                "result": result,
                "a2a_agents_available": len(self.a2a_layer.agent_registry)
            }
        except Exception as e:
            print(f"Local execution failed: {e}")
            
            # If local execution fails and A2A is available, try external agents
            if self.a2a_layer.enabled and self.a2a_layer.agent_registry:
                print("Attempting to delegate to external A2A agents...")
                for agent_name, agent in self.a2a_layer.agent_registry.items():
                    try:
                        a2a_result = await self.a2a_layer.delegate_task(
                            agent_name, task, context
                        )
                        if a2a_result:
                            return {
                                "source": "a2a_external",
                                "agent": agent_name,
                                "result": a2a_result
                            }
                    except Exception as a2a_error:
                        print(f"A2A delegation to {agent_name} failed: {a2a_error}")
                        continue
            
            # If all else fails, return error
            return {
                "source": "error",
                "error": str(e),
                "a2a_agents_available": len(self.a2a_layer.agent_registry)
            }

# Create workflow agents for different scenarios

class FileAnalysisWorkflow(SequentialAgent):
    """Sequential workflow for file analysis: read -> analyze -> report"""
    
    def __init__(self):
        super().__init__(
            name="file_analysis_workflow",
            agents=[
                coordinator.get_agent("file_reader"),
                coordinator.get_agent("git_manager")
            ],
            description="Sequential workflow for analyzing files: file_reader -> git_manager"
        )

class FileCreationWorkflow(SequentialAgent):
    """Sequential workflow for file creation: write -> validate -> commit"""
    
    def __init__(self):
        super().__init__(
            name="file_creation_workflow",
            agents=[
                coordinator.get_agent("file_writer"),
                coordinator.get_agent("git_manager")
            ],
            description="Sequential workflow for creating files: file_writer -> git_manager"
        )

class ParallelFileOperations(ParallelAgent):
    """Parallel workflow for multiple file operations"""
    
    def __init__(self):
        super().__init__(
            name="parallel_file_operations",
            agents=[
                coordinator.get_agent("file_reader"),
                coordinator.get_agent("file_writer"),
                coordinator.get_agent("git_manager")
            ],
            description="Parallel workflow for file operations: file_reader || file_writer || git_manager"
        )

class GitManagementLoop(LoopAgent):
    """Loop workflow for continuous git management"""
    
    def __init__(self):
        super().__init__(
            name="git_management_loop",
            agent=coordinator.get_agent("git_manager"),
            condition="there are uncommitted changes in the workspace",
            description="Loop workflow for git management: git_manager while there are uncommitted changes"
        )

# Create the root agent instance
root_agent = EnhancedFileOperationsAgent()

# Create workflow instances
file_analysis_workflow = FileAnalysisWorkflow()
file_creation_workflow = FileCreationWorkflow()
parallel_file_operations = ParallelFileOperations()
git_management_loop = GitManagementLoop()

# For backward compatibility, also create individual specialized agents
file_reader_agent = coordinator.get_agent("file_reader")
file_writer_agent = coordinator.get_agent("file_writer")
git_manager_agent = coordinator.get_agent("git_manager")
file_coordinator_agent = coordinator.get_agent("file_coordinator") 