# Terminal Agent

**Specialized ADK agent for all shell and terminal operations**

## 💻 Purpose

This agent is the **execution specialist** in the decentralized orchestration pipeline. It handles all shell commands, scripts, and terminal operations safely and efficiently.

## 🎯 Specialization

- **Single Purpose**: Terminal and shell operations only
- **Input**: Tasks requiring command execution or terminal operations
- **Output**: Command results, outputs, and execution status
- **Framework**: Google ADK v1.0.0

## 🔧 How It Works

### 1. **Terminal Task Detection**
Monitors workspace for tasks requiring terminal operations:
- Tasks with `agent_type: "terminal"`
- Tasks with terminal-related descriptions (find, grep, git, npm, pip, etc.)
- Tasks with `specific_commands` provided by planning agents

### 2. **Safe Command Execution**
Executes commands with safety checks:
- **Command validation**: Blocks dangerous operations
- **Timeout protection**: Commands have execution limits
- **Output capture**: Properly captures stdout/stderr
- **Error handling**: Graceful failure management

### 3. **Broad Terminal Capabilities**
Handles any safe terminal operation:
- **File operations**: find, ls, cat, head, tail, grep, awk, sed
- **Development tools**: git, npm, pip, docker, kubectl
- **System commands**: ps, df, du, curl, wget, which
- **Analysis tools**: wc, sort, uniq, diff, md5sum

## 🚀 Example Operations

### **From MetacognitionAgent Planning:**
```json
{
  "specific_commands": [
    "find . -name '*.py' | head -20",
    "find . -name '*.js' | head -20"
  ]
}
```

**TerminalAgent Execution:**
1. Validates commands for safety ✅
2. Executes in sequence with timeout protection
3. Captures outputs: `./src/main.py`, `./lib/utils.py`, etc.
4. Saves results to workspace for next agent

### **Command Sequence Execution:**
```json
{
  "commands": [
    "git status",
    "find . -name '*.py' -exec pylint {} \\;",
    "grep -r 'TODO' --include='*.py' ."
  ]
}
```

## 🛡️ Safety Features

### **Command Validation**
- **Blocked patterns**: `rm -rf /`, `sudo rm`, `format`, `fdisk`
- **Confirmation required**: git operations, installations, chmod 777
- **Safe commands**: All read operations, analysis tools, info commands

### **Execution Protection**
- **Timeout limits**: Commands auto-terminate after timeout
- **Output limits**: 1MB limit on command output
- **Working directory**: Commands run in safe workspace context
- **Error isolation**: Failed commands don't crash the agent

## 📁 Configuration

Uses shared workspace configuration:
- `TASK_WORKSPACE_PATH`: Workspace location (default: `./workspace`)
- `TERMINAL_MODEL`: ADK model (default: `gemini-2.0-flash-live-001`)

## 🎮 Usage

### Standalone
```bash
cd terminal-agent
python -m app.terminal_agent.agent
```

### As Part of Orchestration
Agent runs autonomously and monitors workspace automatically when the orchestration system is active.

## 🔄 Integration

**Workflow Position:**
```
MetacognitionAgent → Detailed Plans → TerminalAgent → Command Results → Next Agent
```

**Dependencies:**
- Requires: Tasks with terminal operations
- Provides: Command execution results
- Communicates: Only via workspace (no direct agent calls)

## 💻 Command Categories

### **File Operations**
```bash
find . -name "*.py"           # File discovery
grep -r "pattern" .           # Text search  
ls -la                        # Directory listing
cat file.txt                  # File content
head -20 file.txt             # First 20 lines
```

### **Development Operations**
```bash
git status                    # Git status
git log --oneline -5          # Recent commits
npm list                      # Node packages
pip list                      # Python packages
```

### **System Analysis**
```bash
ps aux                        # Process list
df -h                         # Disk usage
du -sh *                      # Directory sizes
curl -I https://example.com   # HTTP headers
```

### **Code Analysis**
```bash
find . -name "*.py" | wc -l   # Count Python files
grep -c "function" *.js       # Count functions
pylint module.py              # Code quality
```

This agent provides the reliable execution layer that makes the orchestration system practical - taking detailed plans from MetacognitionAgent and turning them into actual results. 