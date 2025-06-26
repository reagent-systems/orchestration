# 🎛️ Autonomous Agent Orchestration System

A **decentralized multi-agent orchestration platform** built with Google's Agent Development Kit (ADK) that enables autonomous task decomposition, planning, execution, and collaboration through a shared workspace.

> **🎯 Core Concept**: No central orchestrator. Agents self-organize and collaborate through filesystem-based communication, creating a truly autonomous system where complex tasks are recursively broken down and executed by specialized agents.

## 📋 Table of Contents

- [🏗️ System Overview](#️-system-overview)
- [🧩 Agent Architecture](#-agent-architecture) 
- [🚀 Quick Start](#-quick-start)
- [📊 Task Flow & Examples](#-task-flow--examples)
- [🔧 Configuration](#-configuration)
- [🛠️ Troubleshooting](#️-troubleshooting)
- [🚀 Future: Tool Genesis](#-future-tool-genesis)

## 🏗️ System Overview

### Core Principles

#### 🔄 **Decentralized Architecture**
- **No Central Orchestrator**: Agents operate independently
- **Workspace-Based Communication**: All coordination through shared files
- **Self-Organizing**: Agents discover and claim tasks autonomously  
- **Fault-Tolerant**: Individual agent failures don't break the system

#### 🧩 **Recursive Task Decomposition**
- **Goal → Task → Subtask → Action**: True hierarchical breakdown
- **Sequential Dependencies**: Each step builds on previous results
- **Specialized Processing**: Each agent handles specific task types
- **Dynamic Creation**: Tasks can spawn unlimited subtasks

#### 🤖 **Agent Specialization**
- **Single Purpose**: Each agent has one specialized function
- **Real Functionality**: All agents perform actual operations (no simulation)
- **ADK Integration**: Built on Google's Agent Development Kit v1.4.2
- **Workspace Integration**: All agents monitor and update shared workspace

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ TaskBreakdown   │    │ Metacognition   │    │ Terminal        │
│ Agent           │    │ Agent           │    │ Agent           │
│                 │    │                 │    │                 │
│ Decomposes      │    │ Creates         │    │ Executes        │
│ complex tasks   │    │ detailed plans  │    │ shell commands  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   WORKSPACE     │
                    │   (Shared)      │
                    │                 │
                    │ • current_tasks │
                    │ • agent_logs    │
                    │ • results       │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Search          │    │ FileOperations  │    │ [Future Agent]  │
│ Agent           │    │ Agent           │    │                 │
│                 │    │                 │    │ Tool Genesis    │
│ Web searches    │    │ File I/O & Git  │    │ creates new     │
│ using ADK       │    │ operations      │    │ agents on demand│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Directory Structure

```
orchestration/
├── 🤖 AGENTS
│   ├── task-breakdown-agent/     # Decomposes complex tasks
│   ├── metacognition-agent/      # Strategic planning & coordination
│   ├── terminal-agent/           # Shell command execution
│   ├── search-app/              # Web search capabilities
│   └── read-write-app/          # File operations & git
│
├── 📁 WORKSPACE (Shared Communication Layer)
│   ├── current_tasks/           # Active task queue
│   ├── agent_logs/             # Activity history
│   ├── search_results/         # Search outputs
│   └── shared_context/         # Cross-agent memory
│
├── 🔮 FUTURE DEVELOPMENT
│   ├── exploration/            # Research & analysis
│   └── agents_upcoming/        # Tool Genesis system
│
└── 🛠️ UTILITIES
    ├── create_test_task.py     # Task creation tool
    ├── RUN_AGENTS.md          # Quick start guide
    └── .env                   # Configuration
```

## 🧩 Agent Architecture

### 🧩 **TaskBreakdownAgent**
**Purpose**: Decomposes complex tasks into sequential, manageable steps

**Triggers On**:
- Multi-action descriptions ("analyze and compare", "research and apply")
- Tasks containing "and", "then", or workflow indicators
- Complex tasks marked `agent_type: "auto"`

**Example Transformation**:
```
Input: "Analyze codebase for syntax flaws and compare with fixes from Stack Overflow"

Output Subtasks:
1. "Plan analysis strategy for: [original task]" → MetacognitionAgent
2. "Execute analysis based on plan" → TerminalAgent  
3. "Research solutions and fixes for found issues" → SearchAgent
4. "Apply selected solutions" → FileOperationsAgent
```

### 🧠 **MetacognitionAgent**
**Purpose**: Creates detailed execution strategies and coordinates complex workflows

**Triggers On**:
- Tasks with `needs_planning: true`
- Tasks marked `agent_type: "planning"`
- "Stuck" tasks needing re-planning
- Strategic coordination requirements

**Capabilities**:
- 📋 Strategic planning and approach definition
- 📊 Resource requirement analysis  
- ⚠️ Risk assessment and mitigation
- 📈 Progress monitoring and adaptation
- 🔄 Workflow optimization

### 💻 **TerminalAgent**
**Purpose**: Executes shell commands and system operations safely

**Triggers On**:
- Tasks marked `agent_type: "terminal"`
- Commands keywords: "run", "execute", "find", "git", "ls", "grep"
- System-level operations
- Code analysis and execution tasks

**Safety Features**:
- ✅ Command validation and safety checks
- 🚫 Dangerous command blocking (`rm -rf /`, `sudo`, etc.)
- ⏱️ Execution timeouts and resource limits
- 🛡️ Sandboxed execution environment
- 📝 Comprehensive logging

### 🔍 **SearchAgent** 
**Purpose**: Performs web searches using Google ADK's built-in search

**Triggers On**:
- Tasks marked `agent_type: "search"`
- Keywords: "search", "research", "find", "look up", "web search"
- Information gathering and research tasks
- External knowledge requirements

**Features**:
- 🔍 Built-in ADK Google Search (no API keys needed)
- 📊 Result processing and formatting
- 🤝 Workspace integration for result sharing
- 💾 Comprehensive search result storage
- 🎯 Query optimization and refinement

### 📁 **FileOperationsAgent**
**Purpose**: Handles all file system operations and git management

**Triggers On**:
- Tasks marked `agent_type: "file_operations"`
- Keywords: "read", "write", "create", "delete", "save", "file", "directory"
- Git operations and version control
- Code modification and file management

**Capabilities**:
- 📖 File reading, writing, creation, deletion
- 📂 Directory management and organization
- 🔄 Git operations (commit, status, diff, log)
- ⚡ Batch file processing
- 📊 Automatic change tracking and commits

## 🚀 Quick Start

### Prerequisites
```bash
✅ Python 3.9+
✅ Google ADK v1.4.2
✅ Git repository initialized  
✅ Terminal access (5 terminals recommended)
```

### Installation
```bash
# 1. Clone and setup
git clone <repository>
cd orchestration

# 2. Install dependencies  
pip install -r requirements.txt

# 3. Create environment
echo "TASK_WORKSPACE_PATH=./workspace" > .env
echo "GIT_WORKSPACE_PATH=./workspace" >> .env

# 4. Initialize workspace
mkdir -p workspace/{current_tasks,agent_logs,search_results,shared_context}
```

### Running the System

#### 🎯 **Method 1: Individual Terminals (Recommended)**

Open **5 separate terminals** and run each agent:

```bash
# 🧩 Terminal 1 - Task Breakdown Agent
cd task-breakdown-agent/app
python task_breakdown_agent/agent.py

# 🧠 Terminal 2 - Metacognition Agent
cd metacognition-agent/app  
python metacognition_agent/agent.py

# 💻 Terminal 3 - Terminal Agent
cd terminal-agent/app
python terminal_agent/agent.py

# 🔍 Terminal 4 - Search Agent  
cd search-app/app
python google_search_agent/agent.py

# 📁 Terminal 5 - File Operations Agent
cd read-write-app/app
python file_operations_agent/agent.py
```

Each terminal will show:
```
🧩 Starting Task Breakdown Agent...
Specialization: Complex task decomposition
Framework: Google ADK
Workspace monitoring: ENABLED
🔍 task_breakdown_agent monitoring workspace for complex tasks...
```

#### 🧪 **Method 2: Create Test Tasks**

In a 6th terminal:
```bash
# Quick task creation
python create_test_task.py "Analyze codebase for syntax flaws and compare with fixes from Stack Overflow"

# Interactive mode
python create_test_task.py
> Enter task description: Search for Python best practices
> Agent type [auto]: search
✅ Created task: test-task-1234567890-search-for-python
```

#### 👀 **Method 3: Watch the Magic**

1. **File Explorer**: Open `workspace/current_tasks/` and watch:
   - 📄 Task status changes in `task.json` files
   - 📁 New subtasks appearing automatically  
   - 📝 Progress logs updating in real-time
   - 💾 Results being saved by agents

2. **Terminal Output**: Monitor agent activity:
   ```
   🔍 search_agent monitoring workspace...
   🧩 Found complex task: task-xyz-analyze-codebase
   ✅ Completed task breakdown into 4 subtasks
   📝 Created subtask: analyze-strategy-step-01
   ```

## 📊 Task Flow & Examples

### Task Lifecycle
```
created → available → claimed → in_progress → completed
                   ↘          ↗
                    failed ← (retry/abort)
```

### Example Workflows

#### 🔍 **Simple Task: Web Search**
```
Task: "Search for Python best practices"
↓
SearchAgent detects task → Performs Google search → Saves results to workspace/search_results/ → Updates task status: completed
```

#### 🧩 **Complex Task: Full Analysis Workflow**
```
Original Task: "Analyze codebase for syntax flaws and compare with Stack Overflow fixes"
↓
TaskBreakdownAgent creates 4 subtasks:
├── Subtask 1: "Plan analysis strategy" → MetacognitionAgent
├── Subtask 2: "Execute codebase analysis" → TerminalAgent  
├── Subtask 3: "Research Stack Overflow fixes" → SearchAgent
└── Subtask 4: "Apply selected fixes" → FileOperationsAgent
↓
MetacognitionAgent creates detailed strategy → TerminalAgent runs analysis commands → SearchAgent searches for solutions → FileOperationsAgent applies fixes & commits
↓
All subtasks complete → Original task marked completed
```

#### 🔄 **Iterative Refinement**
```
Task gets "stuck" (no progress for 5+ minutes)
↓
MetacognitionAgent detects stuck task
↓
Creates recovery strategy and new approach
↓  
Spawns refined subtasks to overcome blockers
↓
System continues with improved plan
```

### Task JSON Structure
```json
{
  "task_id": "task-1750820004-analyze-codebase",
  "description": "Analyze codebase for syntax flaws and compare with fixes from Stack Overflow",
  "agent_type": "auto",
  "status": "available",
  "priority": 3,
  "created_at": 1750820004.123,
  "created_by": "user",
  "dependencies": [],
  "claimed_by": null,
  "claimed_at": null,
  "completed_at": null,
  "result": null,
  "metadata": {
    "complexity": "high",
    "estimated_minutes": 15
  }
}
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# 📁 Workspace Configuration
TASK_WORKSPACE_PATH=./workspace
GIT_WORKSPACE_PATH=./workspace

# 🤖 Agent Models (defaults to gemini-2.0-flash-live-001)
SEARCH_MODEL=gemini-2.0-flash-live-001
TERMINAL_MODEL=gemini-2.0-flash-live-001
TASK_BREAKDOWN_MODEL=gemini-2.0-flash-live-001
METACOGNITION_MODEL=gemini-2.0-flash-live-001
READ_WRITE_MODEL=gemini-2.0-flash-live-001

# ⏱️ Monitoring & Performance
TASK_MONITOR_INTERVAL=3
LOG_LEVEL=INFO

# 🔍 Google ADK Integration
GOOGLE_API_KEY=your-key-here  # Optional for external APIs
```

### Agent Behavior Tuning

Each agent includes configurable parameters:
- **Task scanning intervals**: How often agents check for new tasks
- **Safety checks**: Command validation and execution limits
- **Retry policies**: How agents handle failures
- **Output formatting**: Result structure and storage

## 🛠️ Troubleshooting

### 🔍 **Common Issues & Solutions**

#### Agents Not Picking Up Tasks
**Symptoms**: Tasks remain in "available" status
```bash
# Check environment
echo $TASK_WORKSPACE_PATH

# Verify workspace structure
ls -la workspace/current_tasks/

# Check agent terminal output for errors
```

#### Tasks Stuck in Processing
**Symptoms**: Tasks claim but never complete
```bash
# Check agent logs
ls -la workspace/agent_logs/

# Monitor specific task
cat workspace/current_tasks/task-xyz/progress.log

# Look for error patterns
grep -r "ERROR" workspace/agent_logs/
```

#### Agent Crashes
**Symptoms**: Agents exit unexpectedly
```bash
# Verify ADK installation
python -c "import google.adk; print('ADK OK')"

# Check Python dependencies
pip install -r requirements.txt

# Run agent manually for debugging
cd task-breakdown-agent/app
python task_breakdown_agent/agent.py
```

#### File Permission Errors  
**Symptoms**: Cannot write to workspace
```bash
# Fix permissions
chmod -R 755 workspace/

# Check git initialization
git status

# Verify write access
touch workspace/test_file && rm workspace/test_file
```

### 🩺 **Health Monitoring**

**Monitor Agent Health**:
1. **Terminal Output**: Watch for error messages and activity
2. **Workspace Activity**: Check for new files and updates
3. **Task Completion**: Monitor success/failure rates
4. **System Resources**: Ensure sufficient CPU/memory

**Debug Mode**:
```bash
export LOG_LEVEL=DEBUG
# Restart agents for verbose logging
```

**Performance Metrics**:
- Task completion rate
- Average task processing time  
- Agent uptime and stability
- Workspace file growth

## 🚀 Future: Tool Genesis

### 🔮 **Next-Generation Agent Creation**

Located in `agents_upcoming/`, the **Tool Genesis System** represents the next evolution:

#### Vision: Agents Creating Agents
The ultimate goal is **recursive agent creation** where agents can synthesize new agents on demand, leading to infinite capability expansion.

#### Planned Agent Network
```
🎯 Agent Synthesizer     - Orchestrates tool creation process
🔍 API Discovery Agent   - Discovers and analyzes external APIs  
⚡ Code Generator Agent  - Writes actual code for new agents
🧩 Template Engine Agent - Manages reusable code patterns
✅ Validation Agent      - Tests and validates generated agents
📦 Dependency Manager    - Handles packages and requirements
🛡️ Security Validator   - Ensures safety and compliance
🚀 Deployment Agent     - Manages agent lifecycle
```

#### Example Tool Genesis Flow
```
User Request: "I need an agent that can manage Docker containers"
↓
Agent Synthesizer → Analyzes requirement
↓  
API Discovery → Finds Docker APIs and documentation
↓
Code Generator → Creates DockerAgent with ADK integration
↓
Validation Agent → Tests the new agent safely
↓
Deployment Agent → Integrates agent into orchestration system
↓
Result: New DockerAgent automatically available for tasks
```

### 🗓️ **Development Roadmap**

**Phase 1** (Current): ✅ Core orchestration system
**Phase 2** (Next): 🔧 Tool Genesis implementation  
**Phase 3** (Future): 🌐 Multi-workspace collaboration
**Phase 4** (Vision): 🤖 Fully autonomous agent ecosystem

## 📚 Related Documentation

- 📖 **`RUN_AGENTS.md`** - Quick start guide for running agents
- 🧪 **`create_test_task.py`** - Tool for creating test tasks  
- 🔬 **`exploration/`** - Research and analysis of orchestration patterns
- 🚀 **`agents_upcoming/`** - Future agent development plans and designs

## 🎯 System Status

**Current Status**: ✅ **Core orchestration system fully functional**

**Verified Capabilities**:
- ✅ Decentralized agent communication through workspace
- ✅ Recursive task decomposition with proper dependencies  
- ✅ Real-time task processing and result sharing
- ✅ Fault-tolerant operation with graceful error handling
- ✅ Multi-agent collaboration on complex workflows
- ✅ Workspace-based coordination without central orchestrator

**Next Milestone**: 🚀 Tool Genesis system implementation

---

**🎛️ Ready to orchestrate? Start with `python create_test_task.py` and watch your agents come alive!** 