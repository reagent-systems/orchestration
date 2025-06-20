# Interface Agent 🎯

**Human Gateway to the Decentralized Multi-Agent Orchestration System**

The Interface Agent provides a user-friendly CLI interface for interacting with the orchestration system. It serves as the primary entry point for humans to assign tasks, monitor progress, and manage the multi-agent ecosystem.

## Features 🚀

### 📝 Task Management
- **Interactive Task Creation**: Guided wizard for creating new tasks
- **Auto-Agent Assignment**: Intelligent agent suggestion based on task content
- **Priority & Complexity Settings**: Categorize tasks for better orchestration
- **Real-time Progress Tracking**: Monitor task execution across all agents

### 👀 System Monitoring  
- **Live Progress Monitor**: Real-time updates of active tasks
- **Agent Status Dashboard**: Health and availability of all agents
- **Task History**: View completed and cancelled tasks
- **System Health**: Workspace statistics and git status

### 🎛️ User Experience
- **Intuitive CLI Menu**: Easy-to-navigate interface
- **Rich Status Display**: Emoji-enhanced status indicators
- **Interactive Wizards**: Step-by-step task creation
- **Live Updates**: Real-time monitoring capabilities

## Architecture 🏗️

```
Human Input → Interface Agent → Shared Workspace → Agent Reactions
```

The Interface Agent follows the **event-driven architecture**:
1. **Human assigns task** via CLI interface
2. **Task written to shared workspace** (git-tracked)
3. **All agents monitor workspace** for new tasks
4. **Agents react autonomously** to relevant tasks
5. **Progress tracked in real-time** via workspace updates

## Usage 🎮

### Starting the Interface Agent

```bash
cd interface-agent
python -m app.interface_agent.agent
```

### Main Menu Options

```
📋 MAIN MENU
1. 📝 Create New Task      - Interactive task creation wizard
2. 👀 View Active Tasks    - List all current tasks  
3. 📊 View Task Progress   - Detailed task information
4. 🤖 View Agent Status    - Agent health dashboard
5. 💾 View Completed Tasks - Task history
6. 🔄 Live Progress Monitor - Real-time updates
7. 🧠 System Health        - System statistics
8. 🚪 Exit                 - Shutdown interface
```

### Task Creation Workflow

1. **Enter Task Details**
   - Title and description
   - Priority level (High/Medium/Low)
   - Complexity (Low/Medium/High)

2. **Agent Assignment**
   - Auto-suggestion based on content
   - Manual agent selection
   - Always includes metacognition agent for planning

3. **Task Deployment**
   - Written to shared workspace
   - Git commit with metadata
   - Agents notified automatically

## Integration 🔗

### Shared Workspace
- **Location**: `./workspace` (configurable via `TASK_WORKSPACE_PATH`)
- **Structure**: Git-tracked task directories
- **Format**: JSON metadata with progress logs

### Agent Communication
- **Event-Driven**: Agents monitor workspace changes
- **Decentralized**: No central orchestrator needed
- **Autonomous**: Agents react independently to tasks

### Configuration
Uses the same environment variables as other agents:
- `TASK_WORKSPACE_PATH`: Workspace location
- All other agent-specific settings from root `.env`

## Task Lifecycle 📋

```
1. Human creates task via Interface Agent
   ↓
2. Task written to workspace/current_tasks/
   ↓  
3. Metacognition Agent analyzes & breaks down task
   ↓
4. Specialized agents execute subtasks
   ↓
5. Progress tracked in shared workspace
   ↓
6. Human monitors via Interface Agent
   ↓
7. Task completion → moved to completed_tasks/
```

## Example Task Creation 💡

```
✨ CREATE NEW TASK
📝 Task Title: Research AI frameworks
📄 Description: Compare LangChain, CrewAI, and AutoGen features
🎯 Priority: Medium
⚡ Complexity: High
🤖 Auto-assigned agents: metacognition_agent, search_agent

✅ Task created: task-2025-06-19-research-ai-frameworks
🔔 Agents notified and beginning processing...
```

## Live Monitoring 📊

The live progress monitor provides real-time updates:
- **Active task status** with progress percentages
- **Agent activity** indicators
- **Auto-refresh** every 2 seconds
- **Ctrl+C** to exit monitor

## Benefits 🎯

✅ **Human-Friendly**: No need to manually edit task files  
✅ **Real-Time Visibility**: Live progress monitoring  
✅ **Event-Driven**: Triggers agent ecosystem reactions  
✅ **Decentralized**: No central orchestrator dependency  
✅ **Git-Integrated**: Full task history and versioning  
✅ **Scalable**: Easy to add more agents to the ecosystem  

## Future Enhancements 🚀

- **Web Interface**: Browser-based dashboard
- **Task Templates**: Predefined task types
- **Agent Performance Metrics**: Detailed analytics
- **Task Dependencies**: Complex workflow management
- **Notification System**: Email/Slack integration
- **API Interface**: Programmatic task creation

---

The Interface Agent bridges the gap between human intent and agent execution, making the powerful orchestration system accessible and manageable through an intuitive interface. 🎯 