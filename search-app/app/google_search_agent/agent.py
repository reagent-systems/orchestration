import os
from google.adk.agents import Agent
from google.adk.tools import google_search
from typing import Optional, Dict, Any
import asyncio

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
            print("A2A integration layer initialized")
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
            print(f"Discovered {len(agents)} external A2A agents")
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

class EnhancedSearchAgent(Agent):
    """Enhanced search agent with A2A integration capabilities"""
    
    def __init__(self, name: str = "enhanced_search_agent", model: str = None):
        # Initialize A2A integration layer
        self.a2a_layer = A2AIntegrationLayer(
            host=os.getenv("A2A_HOST", "localhost"),
            port=int(os.getenv("A2A_PORT", "8080"))
        )
        
        # Set up the agent with Google Search tool
        super().__init__(
            name=name,
            # Use the model from environment or default to a supported live model
            model=model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash-live-001"),
            description="Enhanced agent to answer questions using Google Search and external A2A agents.",
            instruction="""You are an expert researcher with access to both Google Search and external specialized agents. 
            Always stick to the facts and use the most appropriate tool for each task.
            When a task requires specialized capabilities not available through Google Search, 
            consider delegating to external A2A agents if available.""",
            tools=[google_search]
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

# Create the root agent instance
root_agent = EnhancedSearchAgent()

# For backward compatibility, also create the basic agent as shown in the quickstart
basic_search_agent = Agent(
    name="basic_search_agent",
    # Please fill in the latest model id that supports live from
    # https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming/#supported-models
    model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-live-001"),  # for example: model="gemini-2.0-flash-live-001" or model="gemini-2.0-flash-live-preview-04-09"
    description="Agent to answer questions using Google Search.",
    instruction="You are an expert researcher. You always stick to the facts.",
    tools=[google_search]
) 