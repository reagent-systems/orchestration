# 🎛️ Orchestration Interface Agent

**Sophisticated Textual-based Live Orchestration Control Center**

A beautiful, interactive TUI (Terminal User Interface) that provides real-time control over your orchestration system. Built with Textual framework, it offers a Lazygit-style interface for managing tasks and monitoring agents.

## ✨ Features

### 🎯 **Live Task Management**
- **Real-time Task Tree**: Git-style hierarchical view of all tasks
- **Interactive Editing**: Live task modification with agent interruption
- **Status Monitoring**: Visual indicators for task states (available, claimed, in_progress, completed, failed)
- **Quick Actions**: Create, edit, delete tasks with keyboard shortcuts

### 🤖 **Agent Monitoring**
- **Live Agent Status**: Real-time view of all agents and their activities
- **Current Task Tracking**: See which agent is working on which task
- **Agent Interruption**: Automatically signal agents when tasks are modified
- **Performance Metrics**: Activity tracking and status updates

### 🎨 **Beautiful Interface**
- **Multi-Panel Layout**: Task tree, agent status, task details, live logs
- **Color-Coded Status**: Intuitive visual indicators for different states
- **Keyboard Navigation**: Full keyboard control (arrow keys, shortcuts)
- **Modal Dialogs**: Professional task creation and editing forms

### 🔄 **Real-time Features**
- **Live File Watching**: Automatically refresh when workspace changes
- **Auto-refresh**: Updates every 2 seconds
- **Streaming Logs**: Real-time activity feed
- **Instant Feedback**: See changes take effect immediately

## 🚀 Installation

1. **Install Dependencies**:
   ```bash
   cd interface-agent
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   # Ensure .env file has:
   INTERFACE_MODEL=gemini-2.0-flash
   GIT_WORKSPACE_PATH=./workspace
   TASK_MONITOR_INTERVAL=2
   ```

## 🎮 Usage

### Launch the Interface
```bash
# From orchestration root directory
python run_interface.py
```

### Keyboard Shortcuts
| Key | Action | Description |
|-----|--------|-------------|
| `Q` | Quit | Exit the interface |
| `R` | Refresh | Manually refresh all data |
| `N` | New Task | Create a new task |
| `E` | Edit Task | Edit the selected task |
| `D` | Delete Task | Delete the selected task |
| `↑↓` | Navigate | Move through task tree |
| `Tab` | Next Panel | Switch between panels |
| `Space` | Toggle | Expand/collapse tree nodes |

### Interface Layout

```
┌─ 📋 Task Tree ────────────┬─ 🤖 Agent Status ─────────┐
│                           │                           │
│ ⏳ AVAILABLE (2)          │ Agent      Status   Task  │
│ ├─ demo-task-123...       │ Search     Working  demo  │
│ └─ analysis-task-456...   │ Terminal   Idle     -     │
│                           │ File Ops   Idle     -     │
│ 🔄 CLAIMED (1)            │                           │
│ └─ search-task-789...     │                           │
│                           │                           │
│ ⚡ IN_PROGRESS (1)         │                           │
│ └─ terminal-cmd-abc...    │                           │
├───────────────────────────┼───────────────────────────┤
│ 📄 Task Details           │ 📊 Live Logs             │
│                           │                           │
│ 🆔 Task ID: demo-task-123 │ [21:45:32] ✅ Task       │
│ 📝 Description: Search... │           created         │
│ 🤖 Agent Type: search     │ [21:45:35] 🔄 Agent      │
│ 📊 Status: AVAILABLE      │           claimed task    │
│ ⭐ Priority: 3             │ [21:45:38] ⚡ Processing  │
│ 🕐 Created: 2025-06-22    │           started         │
└───────────────────────────┴───────────────────────────┘
```

## 🎯 Key Features in Detail

### Live Task Editing
1. **Select Task**: Navigate to task with arrow keys
2. **Press 'E'**: Opens edit modal dialog
3. **Modify Fields**: Description, agent type, priority
4. **Auto-Interrupt**: Interface signals working agents to stop
5. **Instant Apply**: Changes save immediately to workspace
6. **Agent Reaction**: Agents see changes and re-evaluate task claiming

### Task Creation Workflow
1. **Press 'N'**: Opens new task modal
2. **Fill Details**: Description, preferred agent type, priority
3. **Create**: Task appears immediately in tree
4. **Agent Discovery**: Agents automatically discover and claim suitable tasks

### Real-time Monitoring
- **File Watcher**: Monitors workspace for any changes
- **Auto-refresh**: Updates every 2 seconds
- **Status Tracking**: Live agent status updates
- **Progress Logs**: Streaming activity feed

## 🔧 Technical Details

### Architecture
- **Textual Framework**: Modern TUI framework with rich widgets
- **Async Operations**: Non-blocking file watching and updates
- **Google ADK Integration**: Full agent with workspace tools
- **File System Monitoring**: Watchdog-based workspace monitoring

### Agent Communication
- **Signal Files**: Creates interrupt signals in `workspace/agent_signals/`
- **JSON Tasks**: All tasks stored as JSON in `workspace/current_tasks/`
- **Progress Logs**: Human-readable logs in each task directory
- **Status Updates**: Real-time task status modifications

### Performance
- **Efficient Updates**: Only refreshes changed data
- **Responsive UI**: Smooth keyboard navigation
- **Resource Friendly**: Minimal CPU usage during idle
- **Scalable**: Handles hundreds of tasks efficiently

## 🎨 Customization

### Styling
The interface uses Textual CSS for styling:
- **Colors**: Status-based color coding
- **Layouts**: Flexible panel arrangements
- **Typography**: Clear, readable fonts
- **Animations**: Smooth transitions

### Configuration
Environment variables for customization:
```bash
INTERFACE_MODEL=gemini-2.0-flash    # ADK model
GIT_WORKSPACE_PATH=./workspace      # Workspace location
TASK_MONITOR_INTERVAL=2             # Refresh interval (seconds)
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies installed
   ```bash
   cd interface-agent && pip install -r requirements.txt
   ```

2. **No Tasks Visible**: Check workspace directory exists
   ```bash
   mkdir -p workspace/current_tasks
   ```

3. **Agent Not Responding**: Verify .env configuration
   ```bash
   cp .env.example .env  # Edit with your settings
   ```

4. **Display Issues**: Ensure terminal supports colors
   ```bash
   export TERM=xterm-256color
   ```

## 🎉 Demo

Try the interface with existing tasks:
```bash
# Launch with demo task
python run_interface.py

# Navigate with arrow keys
# Press 'N' to create a new task
# Press 'E' to edit a selected task
# Watch agents react in real-time!
```

---

**🎛️ Experience the future of orchestration control - where every keystroke shapes your agent workflow in real-time!** 