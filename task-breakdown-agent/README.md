# Task Breakdown Agent

**Specialized ADK agent for decomposing complex tasks into sequential steps**

## 🧩 Purpose

This agent is the **first step** in the decentralized orchestration pipeline. It watches the workspace for complex tasks and breaks them down into manageable, sequential subtasks that other specialized agents can handle.

## 🎯 Specialization

- **Single Purpose**: Complex task decomposition only
- **Input**: Complex human tasks (e.g., "analyze codebase for syntax flaws and compare with fixes from Stack Overflow")
- **Output**: Sequential subtasks with proper dependencies and agent assignments
- **Framework**: Google ADK v1.0.0

## 🔧 How It Works

### 1. **Task Detection**
Monitors workspace for tasks with complexity indicators:
- Multiple actions ("analyze **and** compare")
- Analysis tasks ("analyze", "compare") 
- Research combinations ("research and apply")
- Comprehensive tasks ("create comprehensive", "full analysis")

### 2. **Task Breakdown**
Creates 3-7 sequential steps with:
- Clear descriptions
- Agent type assignments (planning, terminal, search, file_operations)
- Dependency chains
- Time estimates

### 3. **Workspace Integration**
- Saves subtasks to `workspace/current_tasks/`
- Creates proper JSON metadata
- Sets up dependency blocking
- Enables other agents to claim subtasks

## 🚀 Example Breakdown

**Input Task:**
```
"analyze codebase for syntax flaws and compare with fixes from Stack Overflow"
```

**Generated Subtasks:**
1. `Plan analysis strategy` → **MetacognitionAgent** (planning)
2. `Execute analysis based on plan` → **TerminalAgent** (depends on #1)
3. `Research syntax error fixes` → **SearchAgent** (depends on #2)
4. `Apply selected fixes` → **FileAgent** (depends on #3)

## 📁 Configuration

Uses shared workspace configuration:
- `TASK_WORKSPACE_PATH`: Workspace location (default: `./workspace`)
- `TASK_BREAKDOWN_MODEL`: ADK model (default: `gemini-2.0-flash-live-001`)

## 🎮 Usage

### Standalone
```bash
cd task-breakdown-agent
python -m app.task_breakdown_agent.agent
```

### As Part of Orchestration
Agent runs autonomously and monitors workspace automatically when the orchestration system is active.

## 🔄 Integration

**Workflow Position:**
```
Human Task → TaskBreakdownAgent → Sequential Subtasks → Specialized Agents
```

**Dependencies:**
- Requires: Shared git workspace
- Provides: Subtasks for other agents
- Communicates: Only via workspace (no direct agent calls)

## 🧠 Intelligence

The agent uses analysis patterns to determine task breakdown strategy:
- **Analysis Workflow**: Plan → Execute → Research → Apply
- **Information Gathering**: Search → Organize
- **Creation Workflow**: Plan → Create
- **General Workflow**: Plan → Execute

This creates consistent, logical task flows that other agents can follow reliably. 