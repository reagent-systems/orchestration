# Orchestration System

A comprehensive multi-agent orchestration system built with Google's Agent Development Kit (ADK) and A2A Protocol integration.

## 🏗️ Architecture

The system consists of three main agents:

1. **Metacognition Agent** - The orchestrator that plans, monitors, and coordinates tasks
2. **Search Agent** - Handles web search and information retrieval
3. **Read-Write Agent** - Manages file operations and git workspace interactions

## 🔧 Configuration

### Centralized Configuration

The system uses a centralized configuration approach with environment variable substitution:

- **Root `.env`** - Contains all shared configuration (API keys, A2A settings, etc.)
- **Agent-specific `.env.example`** - Uses `${VARIABLE_NAME:-default_value}` syntax to reference root configuration

### Setup

1. **Configure Root Environment**:

   ```bash
   # Copy and edit the root .env file
   cp .env.example .env
   # Edit .env with your actual API keys and settings
   ```
2. **Configure Individual Agents**:

   ```bash
   # Each agent directory has its own .env.example
   cd search-app/app
   cp env.example .env
   # The .env file will automatically use values from root .env
   ```

### Configuration Structure

```
orchestration/
├── .env                    # Root configuration (shared)
├── .env.example           # Root configuration template
├── search-app/
│   └── app/
│       ├── env.example    # Uses ${VARIABLE:-default} syntax
│       └── .env          # Agent-specific overrides
├── read-write-app/
│   └── app/
│       ├── env.example    # Uses ${VARIABLE:-default} syntax
│       └── .env          # Agent-specific overrides
└── metacognition-agent/
    └── app/
        ├── env.example    # Uses ${VARIABLE:-default} syntax
        └── .env          # Agent-specific overrides
```

## 🚀 Quick Start

### Option 1: Start with Metacognition Agent (Recommended)

```bash
# 1. Set up root configuration
cp .env.example .env
# Edit .env with your Google API key

# 2. Start metacognition agent
cd metacognition-agent
python -m pip install -r requirements.txt
python -m app.metacognition_agent.agent
```

### Option 2: Start All Agents

```bash
# 1. Set up root configuration
cp .env.example .env
# Edit .env with your Google API key

# 2. Start all agents in separate terminals
# Terminal 1 - Metacognition Agent
cd metacognition-agent && python -m app.metacognition_agent.agent

# Terminal 2 - Search Agent  
cd search-app && python -m app.google_search_agent.agent

# Terminal 3 - Read-Write Agent
cd read-write-app && python -m app.file_operations_agent.agent
```

### Option 3: ADK Web Interface

```bash
# Start the ADK web interface
cd metacognition-agent
python -m google.generativeai.agent
```

## 📁 Project Structure

```
orchestration/
├── .env                           # Root configuration
├── .env.example                   # Root configuration template
├── exploration/                   # Research and analysis
├── metacognition-agent/           # Main orchestrator
├── search-app/                    # Search capabilities
├── read-write-app/               # File operations
└── README.md                     # This file
```

## 🔗 Agent Communication

Agents communicate through:

- **A2A Protocol** - For external agent discovery and coordination
- **HTTP Endpoints** - For direct agent-to-agent communication
- **Git Workspace** - For persistent task tracking and coordination

## 🛠️ Development

### Environment Variables

The system uses environment variable substitution:

- `${VARIABLE_NAME:-default_value}` - Use value from root .env or default
- Individual agents can override any setting in their local `.env`

## 📚 Documentation

- [Metacognition Agent](./metacognition-agent/README.md) - Main orchestrator
- [Search Agent](./search-app/README.md) - Web search capabilities
- [Read-Write Agent](./read-write-app/README.md) - File operations
- [Exploration](./exploration/README.md) - Research and analysis

## 🤝 Contributing

1. Follow the centralized configuration pattern
2. Use `${VARIABLE:-default}` syntax in agent-specific `.env.example` files

# Task Workspace Repository

This is the **separate git repository** for managing orchestration tasks and agent collaboration.

## Repository Purpose

This repository serves as the dedicated workspace for:
- **Task Management**: Version-controlled task definitions and progress
- **Agent Collaboration**: Shared workspace for multi-agent coordination  
- **Progress Tracking**: Historical record of task completion and outcomes
- **Inter-Agent Communication**: Shared context and handoffs between agents

## Directory Structure

```
task-workspace/
├── current_tasks/          # Active tasks being worked on
├── completed_tasks/        # Finished tasks with outcomes
├── shared_context/         # Cross-agent shared information
├── agent_logs/            # Individual agent activity logs
├── collaboration_history/ # Multi-agent coordination records
└── task_templates/        # Reusable task definitions
```

## Git Workflow for Tasks

### Task Lifecycle
1. **Task Creation**: New branch for each major task/goal
2. **Agent Work**: Commits tagged with agent and progress
3. **Collaboration**: Merge branches when agents coordinate
4. **Completion**: Merge to main with task summary

### Commit Convention
```
[AGENT-NAME] Task action: Brief description

- Progress: X% complete
- Status: in-progress|blocked|completed
- Next: What's needed next
- Collaborators: Other agents involved
```

### Branch Strategy
- `main`: Stable completed tasks
- `task/[goal-name]`: Individual task branches
- `collab/[agent1-agent2]`: Agent collaboration branches

## Integration with Main Orchestration Repo

This repository is linked to the main orchestration system via:
- **Git Submodule**: Referenced from main repo
- **Environment Variables**: Path configuration in `.env`
- **Agent Configuration**: All agents point to this shared workspace

## Usage

Agents automatically:
- Clone/pull this repository for task access
- Commit progress with standardized messages
- Create branches for new goals/collaborations
- Merge completed work back to main branch

This separation allows:
- ✅ **Clean task versioning** independent of orchestration code
- ✅ **Shared workspace** across all agents
- ✅ **Task history tracking** with full git capabilities
- ✅ **Collaboration records** between agents
- ✅ **Backup and sync** of task data
