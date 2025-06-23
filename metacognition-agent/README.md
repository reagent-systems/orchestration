# Metacognition Agent - Task Expansion Specialist

**Specialized ADK agent for planning task expansion and stuck task resolution**

## 🧠 Purpose

This agent is the **planning specialist** in the decentralized orchestration pipeline. It takes high-level tasks that need detailed planning and expands them into specific, executable steps with concrete commands and approaches.

## 🎯 Specialization

- **Single Purpose**: Task expansion and detailed planning only
- **Input**: Tasks tagged `needs_planning: true` or stuck/failed tasks
- **Output**: Detailed execution plans with specific commands and approaches
- **Framework**: Google ADK v1.0.0

## 🔧 How It Works

### 1. **Planning Task Detection**
Monitors workspace for tasks that need detailed planning:
- Tasks marked with `needs_planning: true`
- High-level strategy tasks from TaskBreakdownAgent
- Failed/stuck tasks requiring alternative approaches

### 2. **Task Expansion**
Creates detailed, executable steps with:
- Specific commands to run (e.g., `find . -name "*.py"`)
- Expected outputs and success criteria
- Tool suggestions and methodology
- Time estimates and dependencies

### 3. **Stuck Task Resolution**
- Detects failing patterns and loops
- Creates alternative approaches when tasks fail repeatedly
- Provides different tools/methods for same objectives

## 🚀 Example Expansion

**Input Planning Task:**
```
"Plan analysis strategy for: analyze codebase for syntax flaws"
```

**Generated Detailed Steps:**
1. `Identify file types in codebase` → **TerminalAgent**
   - Commands: `find . -name "*.py" | head -20`, `find . -name "*.js" | head -20`
   - Expected: List of Python and JavaScript files
2. `Select linting tools based on file types` → **MetacognitionAgent** (nested planning)
   - Decision criteria: File types from step 1
3. `Define specific error patterns` → **MetacognitionAgent** (nested planning)
   - Focus: Common syntax errors, undefined variables, imports
4. `Execute systematic analysis` → **TerminalAgent**
   - Uses tools and patterns from previous planning

## 🔄 Loop Detection & Resolution

When tasks fail repeatedly:
- **Pattern Analysis**: Identifies why tasks are failing
- **Alternative Strategies**: Creates different approaches
- **Tool Substitution**: Suggests different tools for same goal
- **Simplification**: Breaks complex tasks into smaller chunks

## 📁 Configuration

Uses shared workspace configuration:
- `TASK_WORKSPACE_PATH`: Workspace location (default: `./workspace`)
- `METACOGNITION_MODEL`: ADK model (default: `gemini-2.0-flash-live-001`)

## 🎮 Usage

### Standalone
```bash
cd metacognition-agent
python -m app.metacognition_agent.agent
```

### As Part of Orchestration
Agent runs autonomously and monitors workspace automatically when the orchestration system is active.

## 🔄 Integration

**Workflow Position:**
```
TaskBreakdownAgent → Planning Tasks → MetacognitionAgent → Detailed Steps → Specialized Agents
```

**Dependencies:**
- Requires: Tasks with `needs_planning: true`
- Provides: Detailed execution plans for other agents
- Communicates: Only via workspace (no direct agent calls)

## 🧠 Planning Intelligence

The agent provides different planning strategies:

### **Codebase Analysis Planning**
- File type discovery commands
- Tool selection based on languages found
- Error pattern definition
- Systematic execution approach

### **Research Planning**
- Keyword identification strategies
- Source selection (Stack Overflow, GitHub, docs)
- Search query development
- Result synthesis approaches

### **File Operation Planning**
- Safety-first backup strategies
- Incremental change approaches
- Validation and verification steps

### **Alternative Approach Generation**
- Different tools for same objective
- Simplified execution paths
- Alternative data sources
- Fallback strategies

This creates specific, actionable plans that other agents can execute reliably without needing additional planning. 