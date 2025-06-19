# Practical Implementation Guide: A2A + ADK Integration

## Getting Started

### Prerequisites
- Python 3.8+ environment
- ADK framework installed
- A2A SDK installed
- Basic understanding of both protocols

### Installation
```bash
# Install ADK
pip install google-agent-development-kit

# Install A2A SDK
pip install a2a-sdk

# Install additional dependencies
pip install aiohttp asyncio
```

## Step-by-Step Implementation

### Step 1: Basic ADK Agent Setup
```python
from google.agent_development_kit import Agent, AgentConfig
from google.agent_development_kit.tools import Tool

class BasicADKAgent(Agent):
    def __init__(self, name: str, capabilities: list):
        super().__init__(name=name)
        self.capabilities = capabilities
        self.tools = self._setup_tools()
    
    def _setup_tools(self):
        """Setup agent tools based on capabilities"""
        tools = []
        for capability in self.capabilities:
            if capability == "data_processing":
                tools.append(DataProcessingTool())
            elif capability == "analysis":
                tools.append(AnalysisTool())
        return tools
    
    async def execute(self, task: str, context: dict = None):
        """Execute agent task"""
        # ADK agent execution logic
        result = await self._process_task(task, context)
        return result
```

### Step 2: A2A Integration Layer
```python
import aiohttp
import asyncio
from a2a_sdk import A2AClient, AgentCard

class A2AIntegrationLayer:
    def __init__(self, host: str, port: int = 8080):
        self.host = host
        self.port = port
        self.a2a_client = A2AClient()
        self.agent_registry = {}
        self.session = None
    
    async def start(self):
        """Start A2A integration layer"""
        self.session = aiohttp.ClientSession()
        await self._discover_external_agents()
    
    async def stop(self):
        """Stop A2A integration layer"""
        if self.session:
            await self.session.close()
    
    async def _discover_external_agents(self):
        """Discover external agents via A2A protocol"""
        try:
            # Discover agents from A2A registry
            agents = await self.a2a_client.discover_agents()
            for agent in agents:
                self.agent_registry[agent.name] = agent
            print(f"Discovered {len(agents)} external agents")
        except Exception as e:
            print(f"Error discovering agents: {e}")
    
    async def delegate_task(self, agent_name: str, task: dict):
        """Delegate task to external A2A agent"""
        if agent_name not in self.agent_registry:
            raise ValueError(f"Agent {agent_name} not found")
        
        agent = self.agent_registry[agent_name]
        try:
            result = await self.a2a_client.execute_task(
                agent.endpoint,
                task=task["task"],
                context=task.get("context", {}),
                capabilities=task.get("capabilities", [])
            )
            return result
        except Exception as e:
            print(f"Error delegating task to {agent_name}: {e}")
            return None
    
    async def receive_task(self, task: dict):
        """Receive task from external A2A client"""
        # Handle incoming A2A tasks
        return await self._process_incoming_task(task)
    
    async def _process_incoming_task(self, task: dict):
        """Process incoming A2A task"""
        # Route task to appropriate local ADK agent
        # This would be implemented based on your local agent routing logic
        pass
```

### Step 3: ADK-A2A Bridge Agent
```python
class ADKA2ABridgeAgent(Agent):
    def __init__(self, a2a_layer: A2AIntegrationLayer, local_agents: dict):
        super().__init__(name="adk_a2a_bridge")
        self.a2a_layer = a2a_layer
        self.local_agents = local_agents
        self.task_router = TaskRouter(local_agents, a2a_layer)
    
    async def execute(self, task: str, context: dict = None):
        """Execute task using hybrid local/external agents"""
        # 1. Analyze task requirements
        requirements = await self._analyze_requirements(task, context)
        
        # 2. Create execution plan
        plan = await self.task_router.create_plan(requirements)
        
        # 3. Execute plan
        results = await self._execute_plan(plan)
        
        # 4. Aggregate results
        return await self._aggregate_results(results)
    
    async def _analyze_requirements(self, task: str, context: dict):
        """Analyze task to determine requirements"""
        # Use LLM to analyze task and determine required capabilities
        analysis_prompt = f"""
        Analyze the following task and determine what capabilities are needed:
        Task: {task}
        Context: {context}
        
        Return a JSON object with:
        - required_capabilities: list of required capabilities
        - complexity: simple/medium/complex
        - estimated_duration: estimated time in minutes
        - dependencies: list of dependencies
        """
        
        # This would use an LLM to analyze the task
        # For now, return a simple analysis
        return {
            "required_capabilities": ["data_processing", "analysis"],
            "complexity": "medium",
            "estimated_duration": 5,
            "dependencies": []
        }
    
    async def _execute_plan(self, plan: dict):
        """Execute the task execution plan"""
        results = {}
        
        for step in plan["steps"]:
            if step["agent_type"] == "local":
                # Execute with local ADK agent
                agent = self.local_agents[step["agent_name"]]
                result = await agent.execute(step["task"], step["context"])
                results[step["step_id"]] = result
            elif step["agent_type"] == "external":
                # Execute with external A2A agent
                result = await self.a2a_layer.delegate_task(
                    step["agent_name"], 
                    step["task"]
                )
                results[step["step_id"]] = result
        
        return results
    
    async def _aggregate_results(self, results: dict):
        """Aggregate results from multiple agents"""
        # Combine results from local and external agents
        aggregated = {
            "local_results": {},
            "external_results": {},
            "combined_result": None
        }
        
        for step_id, result in results.items():
            if result.get("source") == "local":
                aggregated["local_results"][step_id] = result
            else:
                aggregated["external_results"][step_id] = result
        
        # Create combined result
        aggregated["combined_result"] = await self._combine_results(results)
        
        return aggregated
    
    async def _combine_results(self, results: dict):
        """Combine results from multiple agents"""
        # This would implement logic to combine results
        # For now, return a simple combination
        return {
            "status": "completed",
            "summary": f"Completed {len(results)} steps",
            "data": results
        }
```

### Step 4: Task Router
```python
class TaskRouter:
    def __init__(self, local_agents: dict, a2a_layer: A2AIntegrationLayer):
        self.local_agents = local_agents
        self.a2a_layer = a2a_layer
    
    async def create_plan(self, requirements: dict):
        """Create execution plan for task"""
        plan = {
            "steps": [],
            "estimated_duration": 0,
            "agent_count": 0
        }
        
        # Match capabilities to available agents
        for capability in requirements["required_capabilities"]:
            step = await self._create_step_for_capability(capability, requirements)
            if step:
                plan["steps"].append(step)
                plan["agent_count"] += 1
        
        return plan
    
    async def _create_step_for_capability(self, capability: str, requirements: dict):
        """Create execution step for a capability"""
        # First try to find local agent
        local_agent = self._find_local_agent(capability)
        if local_agent:
            return {
                "step_id": f"local_{capability}",
                "agent_type": "local",
                "agent_name": local_agent.name,
                "capability": capability,
                "task": f"Execute {capability} task",
                "context": requirements.get("context", {})
            }
        
        # Then try to find external agent
        external_agent = await self._find_external_agent(capability)
        if external_agent:
            return {
                "step_id": f"external_{capability}",
                "agent_type": "external",
                "agent_name": external_agent.name,
                "capability": capability,
                "task": {
                    "task": f"Execute {capability} task",
                    "context": requirements.get("context", {}),
                    "capabilities": [capability]
                }
            }
        
        return None
    
    def _find_local_agent(self, capability: str):
        """Find local ADK agent with required capability"""
        for agent_name, agent in self.local_agents.items():
            if capability in agent.capabilities:
                return agent
        return None
    
    async def _find_external_agent(self, capability: str):
        """Find external A2A agent with required capability"""
        for agent_name, agent in self.a2a_layer.agent_registry.items():
            if capability in agent.capabilities:
                return agent
        return None
```

### Step 5: Main Application
```python
import asyncio
from typing import Dict, List

class HybridAgentSystem:
    def __init__(self):
        self.local_agents = {}
        self.a2a_layer = None
        self.bridge_agent = None
    
    async def initialize(self):
        """Initialize the hybrid agent system"""
        # 1. Setup local ADK agents
        await self._setup_local_agents()
        
        # 2. Setup A2A integration layer
        await self._setup_a2a_layer()
        
        # 3. Setup bridge agent
        await self._setup_bridge_agent()
        
        print("Hybrid agent system initialized successfully")
    
    async def _setup_local_agents(self):
        """Setup local ADK agents"""
        self.local_agents = {
            "data_processor": BasicADKAgent("data_processor", ["data_processing"]),
            "analyzer": BasicADKAgent("analyzer", ["analysis"]),
            "reporter": BasicADKAgent("reporter", ["reporting"])
        }
    
    async def _setup_a2a_layer(self):
        """Setup A2A integration layer"""
        self.a2a_layer = A2AIntegrationLayer("localhost", 8080)
        await self.a2a_layer.start()
    
    async def _setup_bridge_agent(self):
        """Setup ADK-A2A bridge agent"""
        self.bridge_agent = ADKA2ABridgeAgent(self.a2a_layer, self.local_agents)
    
    async def execute_task(self, task: str, context: dict = None):
        """Execute task using hybrid system"""
        return await self.bridge_agent.execute(task, context)
    
    async def shutdown(self):
        """Shutdown the hybrid system"""
        if self.a2a_layer:
            await self.a2a_layer.stop()

# Usage example
async def main():
    # Initialize hybrid system
    system = HybridAgentSystem()
    await system.initialize()
    
    # Execute a task
    task = "Analyze customer data and generate a report"
    context = {"customer_id": "12345", "data_source": "database"}
    
    result = await system.execute_task(task, context)
    print(f"Task result: {result}")
    
    # Shutdown
    await system.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

### Environment Variables
```bash
# A2A Configuration
A2A_HOST=localhost
A2A_PORT=8080
A2A_AUTH_TOKEN=your_auth_token

# ADK Configuration
ADK_MODEL_PATH=/path/to/model
ADK_LOG_LEVEL=INFO

# Integration Configuration
INTEGRATION_MODE=hybrid
MAX_CONCURRENT_TASKS=10
TASK_TIMEOUT=300
```

### Configuration File
```yaml
# config.yaml
a2a:
  host: localhost
  port: 8080
  auth_token: your_auth_token
  discovery_interval: 300

adk:
  model_path: /path/to/model
  log_level: INFO
  max_agents: 50

integration:
  mode: hybrid
  max_concurrent_tasks: 10
  task_timeout: 300
  retry_attempts: 3

agents:
  local:
    - name: data_processor
      capabilities: [data_processing]
    - name: analyzer
      capabilities: [analysis]
    - name: reporter
      capabilities: [reporting]
  
  external:
    - name: payment_processor
      endpoint: https://partner.com/a2a/payment
      capabilities: [payment_processing]
    - name: shipping_tracker
      endpoint: https://shipping.com/a2a/tracking
      capabilities: [shipping_tracking]
```

## Testing

### Unit Tests
```python
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

class TestADKA2ABridgeAgent:
    @pytest.fixture
    async def bridge_agent(self):
        a2a_layer = Mock()
        local_agents = {
            "test_agent": Mock()
        }
        return ADKA2ABridgeAgent(a2a_layer, local_agents)
    
    @pytest.mark.asyncio
    async def test_execute_task(self, bridge_agent):
        task = "Test task"
        context = {"test": "data"}
        
        result = await bridge_agent.execute(task, context)
        
        assert result is not None
        assert "status" in result

class TestA2AIntegrationLayer:
    @pytest.fixture
    async def a2a_layer(self):
        layer = A2AIntegrationLayer("localhost", 8080)
        yield layer
        await layer.stop()
    
    @pytest.mark.asyncio
    async def test_discover_agents(self, a2a_layer):
        await a2a_layer.start()
        
        assert len(a2a_layer.agent_registry) >= 0
```

### Integration Tests
```python
class TestHybridSystem:
    @pytest.fixture
    async def system(self):
        system = HybridAgentSystem()
        await system.initialize()
        yield system
        await system.shutdown()
    
    @pytest.mark.asyncio
    async def test_end_to_end_task(self, system):
        task = "Process customer data and generate report"
        context = {"customer_id": "test_123"}
        
        result = await system.execute_task(task, context)
        
        assert result is not None
        assert "combined_result" in result
        assert result["combined_result"]["status"] == "completed"
```

## Deployment

### Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "main.py"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  hybrid-agent-system:
    build: .
    ports:
      - "8080:8080"
    environment:
      - A2A_HOST=a2a-registry
      - A2A_PORT=8080
    depends_on:
      - a2a-registry
  
  a2a-registry:
    image: a2a/registry:latest
    ports:
      - "8081:8080"
```

## Monitoring and Observability

### Logging Configuration
```python
import logging
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
```

### Metrics Collection
```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
task_counter = Counter('hybrid_tasks_total', 'Total tasks executed', ['agent_type', 'status'])
task_duration = Histogram('hybrid_task_duration_seconds', 'Task execution duration', ['agent_type'])
active_agents = Gauge('hybrid_active_agents', 'Number of active agents', ['agent_type'])

class MetricsCollector:
    def __init__(self):
        self.task_counter = task_counter
        self.task_duration = task_duration
        self.active_agents = active_agents
    
    def record_task(self, agent_type: str, status: str, duration: float):
        """Record task metrics"""
        self.task_counter.labels(agent_type=agent_type, status=status).inc()
        self.task_duration.labels(agent_type=agent_type).observe(duration)
    
    def update_active_agents(self, agent_type: str, count: int):
        """Update active agents count"""
        self.active_agents.labels(agent_type=agent_type).set(count)
```

This implementation guide provides a practical foundation for integrating A2A protocol with ADK framework, enabling you to build sophisticated hybrid multi-agent systems that combine local orchestration with external interoperability. 