# Conscientious Planning Metacognition Agent

This is a sophisticated metacognition agent system that provides conscientious planning, internal monologue capabilities, and git-based task tracking for intelligent orchestration of multi-agent systems.

## 🧠 Core Concept

The **Conscientious Planning Metacognition Agent** acts as the "brain" of the orchestration system, providing:

- **Internal Monologue**: Continuous self-reflection and metacognitive analysis
- **Conscientious Planning**: Careful task decomposition and strategic planning  
- **Git-Based Task Tracking**: Complete audit trail of all orchestration steps
- **Agent Orchestration**: Coordination of search_agent and read_write_agent
- **Progress Monitoring**: Real-time tracking of task completion and bottlenecks

## 🏗️ Architecture

### Metacognition Engine
- **Self-Reflection**: Analyzes task progress, agent performance, and strategy effectiveness
- **Internal Monologue**: Continuous thinking and analysis capabilities
- **Progress Tracking**: Monitors completion status and identifies bottlenecks
- **Strategy Assessment**: Evaluates and adjusts execution strategies

### Git-Based Task Tracking
- **Complete Audit Trail**: Every orchestration step is committed to git
- **Task Branches**: Each task gets its own git branch for isolation
- **Step History**: Individual steps are tracked with commit hashes
- **Progress Visualization**: Git history shows the complete task lifecycle

### Multi-Agent Coordination
- **Task Planner**: Decomposes complex tasks into manageable steps
- **Progress Monitor**: Tracks real-time progress and identifies issues
- **Agent Orchestrator**: Coordinates and executes agent actions
- **Reflection Engine**: Analyzes outcomes and generates insights

## 📁 Project Structure

```
metacognition-agent/
├── app/
│   ├── env.example              # Environment configuration template
│   └── metacognition_agent/
│       ├── __init__.py          # Package initialization
│       ├── agent.py             # Main metacognition agent
│       ├── tools.py             # Orchestration tools
│       ├── coordinator.py       # Multi-agent coordinator
│       ├── metacognition.py     # Metacognition engine
│       └── task_tracker.py      # Git-based task tracking
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Features

### Internal Monologue Capabilities
- **Task Analysis**: Reflects on task progress and completion status
- **Strategy Reflection**: Analyzes effectiveness of current approaches
- **Agent Performance**: Monitors individual agent effectiveness
- **Bottleneck Analysis**: Identifies and addresses system constraints
- **Completion Assessment**: Evaluates task completion quality

### Git-Based Task Tracking
- **Task Creation**: Each task gets a unique git branch
- **Step Commits**: Every orchestration step is committed to git
- **Progress History**: Complete audit trail of task execution
- **Branch Management**: Isolated task branches for parallel execution
- **Commit Messages**: Descriptive commit messages for each step

### Agent Orchestration
- **Task Decomposition**: Breaks complex tasks into manageable steps
- **Agent Assignment**: Assigns appropriate agents to each step
- **Execution Monitoring**: Tracks step execution and results
- **Failure Handling**: Manages agent failures and retries
- **Resource Optimization**: Optimizes agent resource allocation

### Workflow Agents
- **Sequential Workflows**: Complete task lifecycle orchestration
- **Parallel Workflows**: Concurrent monitoring and execution
- **Loop Workflows**: Continuous reflection and analysis

## 🛠️ Setup Instructions

### 1. Environment Setup

Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate (each new terminal)
# macOS/Linux: source .venv/bin/activate
# Windows CMD: .venv\Scripts\activate.bat
# Windows PowerShell: .venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configuration

Copy the environment template and configure your settings:

```bash
cd app
cp env.example .env
```

Edit `.env` with your configuration:

```bash
# ADK Configuration
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_actual_api_key_here

# Metacognition Agent Configuration
METACOGNITION_AGENT_NAME=conscientious_planner
METACOGNITION_MODEL=gemini-2.0-flash-live-001
ENABLE_INTERNAL_MONOLOGUE=true
ENABLE_PROGRESS_TRACKING=true
ENABLE_TASK_ORCHESTRATION=true

# Git-Based Task Tracking
TASK_WORKSPACE_PATH=./task_workspace
TASK_GIT_REPO_URL=your_task_repo_url_here
TASK_BRANCH=main
TASK_COMMIT_PREFIX=[Orchestration]
AUTO_COMMIT_TASKS=true
TASK_HISTORY_RETENTION_DAYS=30

# Agent Orchestration Configuration
ENABLE_AGENT_ORCHESTRATION=true
ORCHESTRATION_TIMEOUT_SECONDS=300
MAX_CONCURRENT_AGENTS=5
AGENT_RETRY_ATTEMPTS=3
AGENT_FALLBACK_ENABLED=true

# Available Agent Endpoints
SEARCH_AGENT_ENDPOINT=http://localhost:8001/search_agent
READ_WRITE_AGENT_ENDPOINT=http://localhost:8002/file_operations_agent
EXTERNAL_A2A_AGENTS_ENABLED=true

# Task Planning Configuration
PLANNING_STRATEGY=adaptive
TASK_DECOMPOSITION_ENABLED=true
PROGRESS_MONITORING_INTERVAL=30
TASK_COMPLETION_THRESHOLD=0.95
METACOGNITION_REFLECTION_INTERVAL=60

# Internal Monologue Configuration
MONOLOGUE_LOG_LEVEL=INFO
MONOLOGUE_PERSISTENCE=true
MONOLOGUE_ANALYSIS_ENABLED=true
SELF_REFLECTION_ENABLED=true
```

## 🎯 Usage Examples

### Basic Task Orchestration

```python
from metacognition_agent.agent import root_agent

# Orchestrate a complete task
result = await root_agent.orchestrate_task(
    user_request="Research the latest AI developments and create a comprehensive report",
    task_description="AI Research and Report Generation"
)

print(f"Task completed: {result['status']}")
print(f"Completion: {result['completion_percentage']}%")
```

### Using Individual Agents

```python
from metacognition_agent.agent import (
    task_planner_agent,
    progress_monitor_agent,
    agent_orchestrator_agent,
    reflection_engine_agent
)

# Plan a task
plan_result = await task_planner_agent.execute("Create a plan for data analysis project")

# Monitor progress
progress_result = await progress_monitor_agent.execute("Monitor active tasks")

# Execute orchestration
orchestration_result = await agent_orchestrator_agent.execute("Execute pending steps")

# Reflect on outcomes
reflection_result = await reflection_engine_agent.execute("Analyze recent task completions")
```

### Using Workflow Agents

```python
from metacognition_agent.agent import (
    task_orchestration_workflow,
    parallel_orchestration_workflow,
    continuous_reflection_workflow
)

# Complete task lifecycle
result = await task_orchestration_workflow.execute("Complete research project")

# Parallel monitoring and execution
result = await parallel_orchestration_workflow.execute("Monitor and execute tasks")

# Continuous reflection
result = await continuous_reflection_workflow.execute("Analyze system performance")
```

## 🔍 Git-Based Task Tracking

### Task History

Each task creates a git branch with complete execution history:

```bash
# View task branches
git branch -a

# Checkout a specific task
git checkout task/abc12345

# View task history
git log --oneline

# View step details
git show <commit-hash>
```

### Task Structure

```
task_workspace/
├── tasks/
│   └── <task-id>/
│       ├── task.json              # Task metadata
│       ├── progress.json          # Current progress
│       └── steps/
│           ├── step_001.json      # Step 1 details
│           ├── step_002.json      # Step 2 details
│           └── ...
└── README.md                      # Repository documentation
```

## 🧠 Metacognitive Capabilities

### Internal Monologue Types

1. **Task Analysis**: Reflects on specific task progress
2. **Progress Evaluation**: Analyzes overall system progress
3. **Strategy Reflection**: Evaluates execution strategies
4. **Agent Performance**: Monitors individual agent effectiveness
5. **Bottleneck Analysis**: Identifies system constraints
6. **Completion Assessment**: Evaluates task completion quality

### Reflection Examples

```python
from metacognition_agent.metacognition import metacognition_engine, ReflectionType

# Reflect on task progress
await metacognition_engine.reflect_on_task("task_123", "Research project")

# Analyze bottlenecks
await metacognition_engine.analyze_bottlenecks()

# Assess completion
await metacognition_engine.assess_completion("task_123")

# Get recent thoughts
thoughts = metacognition_engine.get_recent_thoughts(10)
```

## 🔧 Configuration Options

### Metacognition Settings
- `ENABLE_INTERNAL_MONOLOGUE`: Enable metacognitive reflection
- `METACOGNITION_REFLECTION_INTERVAL`: Reflection frequency (seconds)
- `MONOLOGUE_LOG_LEVEL`: Logging detail level
- `SELF_REFLECTION_ENABLED`: Enable self-analysis

### Task Tracking Settings
- `TASK_WORKSPACE_PATH`: Git repository location
- `AUTO_COMMIT_TASKS`: Automatic git commits
- `TASK_HISTORY_RETENTION_DAYS`: How long to keep task history
- `TASK_COMMIT_PREFIX`: Git commit message prefix

### Orchestration Settings
- `ORCHESTRATION_TIMEOUT_SECONDS`: Task timeout
- `MAX_CONCURRENT_AGENTS`: Maximum parallel agents
- `AGENT_RETRY_ATTEMPTS`: Retry attempts for failed steps
- `TASK_COMPLETION_THRESHOLD`: Completion percentage threshold

## 🎬 Demo Examples

### Complex Task Orchestration

```python
# Research and document creation
result = await root_agent.orchestrate_task(
    "Research quantum computing developments, gather recent papers, and create a comprehensive technical report with code examples"
)

# Multi-step project setup
result = await root_agent.orchestrate_task(
    "Set up a complete development environment for a machine learning project, including data collection, preprocessing, and model training pipeline"
)

# Analysis and reporting
result = await root_agent.orchestrate_task(
    "Analyze the current codebase, identify technical debt, create refactoring recommendations, and generate a detailed report"
)
```

### Voice/Video Commands

- "Orchestrate a research project on AI safety"
- "Create a complete development environment setup"
- "Analyze and optimize the current system architecture"
- "Generate a comprehensive technical documentation"

## 🔍 Monitoring and Analytics

### System Health Monitoring

```python
# Get orchestration status
status = await root_agent.get_orchestration_status()

print(f"Active tasks: {status['system_health']['active_tasks']}")
print(f"Total tasks: {status['system_health']['total_tasks']}")
print(f"Git commits: {status['system_health']['git_commits']}")
print(f"Metacognitive thoughts: {status['system_health']['metacognition_thoughts']}")
```

### Agent Performance Analytics

```python
# Get agent performance
performance = metacognition_tools.get_agent_performance()

for agent, metrics in performance['agent_performance'].items():
    print(f"{agent}: {metrics['success_rate']:.1%} success rate")
    print(f"  Avg response time: {metrics['avg_response_time']:.2f}s")
    print(f"  Total tasks: {metrics['total_tasks']}")
```

## 🚀 Next Steps

- **Enhanced Planning**: More sophisticated task decomposition algorithms
- **Learning Capabilities**: Learn from past orchestration patterns
- **Predictive Analytics**: Predict task completion times and resource needs
- **Advanced Visualization**: Git history visualization and progress dashboards
- **Integration APIs**: REST APIs for external system integration

## 📚 Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [LLM Agents](https://google.github.io/adk-docs/agents/llm-agents/)
- [Workflow Agents](https://google.github.io/adk-docs/agents/workflow-agents/)
- [Multi-Agent Systems](https://google.github.io/adk-docs/agents/multi-agents/)
- [A2A Protocol](https://github.com/google-a2a/A2A)

## 🎯 Key Benefits

1. **Complete Transparency**: Every step tracked in git
2. **Intelligent Planning**: Metacognitive task decomposition
3. **Self-Improvement**: Continuous reflection and learning
4. **Reliable Execution**: Conscientious progress monitoring
5. **Audit Trail**: Full history of orchestration decisions
6. **Scalable Architecture**: Multi-agent coordination system

The Conscientious Planning Metacognition Agent represents a new paradigm in AI orchestration, combining the power of metacognition with the reliability of git-based tracking to create a truly intelligent and transparent system. 