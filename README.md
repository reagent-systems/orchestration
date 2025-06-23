# 🎛️ Orchestration System - Live Agent Control Center

**Sophisticated Multi-Agent Orchestration with Real-time Interactive Control**

A decentralized multi-agent system powered by Google ADK v1.4.2, featuring autonomous task management and a beautiful Textual-based control interface. Watch agents collaborate in real-time through an elegant TUI inspired by Lazygit.

## 🚀 Quick Start

### 1. **Prerequisites**
```bash
# Ensure you have Python 3.9+ and pip installed
python --version  # Should be 3.9+
pip --version
```

### 2. **Clone & Setup**
```bash
# Clone the repository (if needed)
cd orchestration

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r interface-agent/requirements.txt
pip install -r search-app/requirements.txt
pip install -r read-write-app/requirements.txt
pip install -r metacognition-agent/requirements.txt
pip install -r task-breakdown-agent/requirements.txt
pip install -r terminal-agent/requirements.txt
```

### 3. **Configure Environment**
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your preferences (optional - defaults work fine)
# The system works out-of-the-box with default settings
```

### 4. **Launch the Control Center** 🎛️
```bash
# Start the interactive interface
python run_interface.py
```

**That's it!** The beautiful TUI interface will launch and you can immediately:
- ✨ Create tasks with `N`
- 🔍 Edit tasks with `E` 
- 👀 Watch agents work in real-time
- 🎮 Control everything with keyboard shortcuts

## 🎯 What You'll See

### **Interface Layout**
```
┌─ 📋 Task Tree ────────────┬─ 🤖 Agent Status ─────────┐
│ ⏳ AVAILABLE (1)          │ Agent      Status   Task  │
│ └─ demo-task-123...       │ Search     Idle     -     │
│                           │ Terminal   Idle     -     │
│ 🔄 CLAIMED (0)            │ File Ops   Idle     -     │
│                           │ Planning   Idle     -     │
│ ⚡ IN_PROGRESS (0)         │ Breakdown  Idle     -     │
│                           │                           │
│ ✅ COMPLETED (0)          │                           │
├───────────────────────────┼───────────────────────────┤
│ 📄 Task Details           │ 📊 Live Logs             │
│ Select a task to view...  │ [Ready for tasks...]      │
└───────────────────────────┴───────────────────────────┘
```

### **Keyboard Controls**
| Key | Action | Description |
|-----|--------|-------------|
| `N` | **New Task** | Create a task via modal dialog |
| `E` | **Edit Task** | Modify selected task (interrupts agents!) |
| `D` | **Delete Task** | Remove selected task |
| `↑↓` | **Navigate** | Move through task tree |
| `R` | **Refresh** | Manual data refresh |
| `Q` | **Quit** | Exit interface |

## 🎬 Demo Workflow

### **Try This Example:**

1. **Launch Interface**: `python run_interface.py`

2. **Create a Complex Task** (Press `N`):
   ```
   Description: "Analyze codebase for syntax flaws and search Stack Overflow for fixes"
   Agent Type: auto
   Priority: 3
   ```

3. **Watch the Magic** ✨:
   - TaskBreakdownAgent decomposes it into steps
   - MetacognitionAgent creates execution plans
   - TerminalAgent analyzes your code
   - SearchAgent finds solutions online
   - FileAgent implements fixes

4. **Edit Tasks Live** (Select task, Press `E`):
   - Modify description mid-execution
   - Watch agents stop and adapt instantly
   - See real-time coordination

## 🤖 Available Agents

| Agent | Purpose | Capabilities |
|-------|---------|-------------|
| **🎛️ Interface** | Control Center | Live task management, agent monitoring |
| **📊 TaskBreakdown** | Task Analysis | Decomposes complex tasks into steps |
| **🧠 Metacognition** | Planning | Creates detailed execution strategies |
| **🖥️ Terminal** | Shell Operations | Safe command execution with validation |
| **🔍 Search** | Web Research | Built-in Google Search via ADK |
| **📁 FileOperations** | File Management | Real filesystem operations |

## 🎯 Use Cases

### **Development Tasks**
```
"Review code quality and suggest improvements"
→ Terminal analyzes code
→ Search finds best practices  
→ File creates improvement plan
```

### **Research Tasks**
```
"Research latest Python frameworks and create comparison"
→ Search gathers information
→ Metacognition organizes findings
→ File creates structured report
```

### **System Administration**
```
"Check system health and optimize performance"
→ Terminal runs diagnostics
→ Search finds optimization tips
→ File documents results
```

## 🔧 Advanced Usage

### **Running Individual Agents**
If you want to run agents separately:

```bash
# Terminal Agent
cd terminal-agent && python app/terminal_agent/agent.py

# Search Agent  
cd search-app && python app/google_search_agent/agent.py

# File Operations Agent
cd read-write-app && python app/file_operations_agent/agent.py

# Planning Agent
cd metacognition-agent && python app/metacognition_agent/agent.py

# Task Breakdown Agent
cd task-breakdown-agent && python app/task_breakdown_agent/agent.py
```

### **Workspace Structure**
```
workspace/
├── current_tasks/          # Active tasks (JSON + logs)
├── completed_tasks/        # Finished tasks
├── agent_logs/            # Agent activity logs  
├── agent_signals/         # Interrupt signals
└── search_results/        # Search findings
```

### **Environment Variables**
```bash
# Model Configuration
SEARCH_MODEL=gemini-2.0-flash
METACOGNITION_MODEL=gemini-2.0-flash
TASK_BREAKDOWN_MODEL=gemini-2.0-flash
TERMINAL_MODEL=gemini-2.0-flash
FILE_OPERATIONS_MODEL=gemini-2.0-flash
INTERFACE_MODEL=gemini-2.0-flash

# System Configuration  
GIT_WORKSPACE_PATH=./workspace
TASK_MONITOR_INTERVAL=3
```

## 🚨 Troubleshooting

### **Common Issues**

**1. Interface won't start**
```bash
# Install missing dependencies
cd interface-agent && pip install -r requirements.txt

# Check Python version
python --version  # Need 3.9+
```

**2. No agents responding**
```bash
# Verify environment
cat .env  # Check configuration

# Test workspace
ls -la workspace/current_tasks/
```

**3. Import errors**
```bash
# Reinstall ADK
pip install google-adk==1.4.2

# Check virtual environment
which python  # Should be in venv/
```

**4. Terminal display issues**
```bash
# Fix terminal colors
export TERM=xterm-256color

# Resize terminal (recommended: 120x40 minimum)
```

### **Debugging Mode**
```bash
# Run with verbose output
PYTHONPATH=. python -v run_interface.py

# Check agent logs
tail -f workspace/agent_logs/*.log
```

## 🎉 Success Indicators

**You'll know it's working when:**
- ✅ Interface launches with beautiful TUI
- ✅ Demo task appears in task tree
- ✅ Creating new tasks works (`N` key)
- ✅ Agents show as "Idle" in status panel
- ✅ Editing tasks opens modal dialog (`E` key)
- ✅ Live logs show activity

## 🔗 Architecture

```
Human Input → Interface Agent → Workspace → Agent Ecosystem
     ↑              ↓              ↓            ↓
  Live TUI ← Live Monitoring ← Task Files ← Autonomous Agents
```

**Key Features:**
- 🎯 **Decentralized**: No central orchestrator
- ⚡ **Real-time**: Live task editing and monitoring  
- 🤖 **Autonomous**: Agents self-coordinate via workspace
- 🛡️ **Safe**: Command validation and error handling
- 🎨 **Beautiful**: Professional TUI interface

## 📚 Learn More

- **[Interface Agent](interface-agent/README.md)** - Detailed TUI documentation
- **[Search Agent](search-app/README.md)** - Google Search integration
- **[Terminal Agent](terminal-agent/README.md)** - Safe command execution
- **[File Agent](read-write-app/README.md)** - Filesystem operations

---

**🎛️ Experience the future of orchestration - where intelligent agents collaborate seamlessly through an elegant interface you control in real-time!**

**Ready? Just run:** `python run_interface.py` **and start orchestrating!** 🚀 