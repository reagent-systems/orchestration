# 🤖 Individual Agent Testing Guide

This is the clean, simple approach to test fundamental orchestration.

## 🎯 Goal
Run each agent in a separate terminal window and watch them autonomously tackle tasks through the file explorer.

## 📁 Current Clean Structure
```
orchestration/
├── search-app/           # Google Search Agent
├── read-write-app/       # File Operations Agent  
├── metacognition-agent/  # Planning & Strategy Agent
├── task-breakdown-agent/ # Task Decomposition Agent
├── terminal-agent/       # Command Execution Agent
├── workspace/            # Shared task workspace
├── exploration/          # (preserved)
└── agents_upcoming/      # (preserved)
```

## 🚀 How to Run Agents

### 1. **Terminal 1 - Task Breakdown Agent**
```bash
cd task-breakdown-agent/app
python task_breakdown_agent/agent.py
```
**Purpose**: Breaks complex tasks into sequential steps

### 2. **Terminal 2 - Metacognition Agent** 
```bash
cd metacognition-agent/app
python metacognition_agent/agent.py
```
**Purpose**: Creates detailed plans and strategies

### 3. **Terminal 3 - Terminal Agent**
```bash
cd terminal-agent/app  
python terminal_agent/agent.py
```
**Purpose**: Executes shell commands and scripts

### 4. **Terminal 4 - Search Agent**
```bash
cd search-app/app
python google_search_agent/agent.py
```
**Purpose**: Performs web searches using Google ADK

### 5. **Terminal 5 - File Operations Agent**
```bash
cd read-write-app/app
python file_operations_agent/agent.py
```
**Purpose**: Handles file reading, writing, and git operations

## 📋 Creating a Test Task

In a 6th terminal, create a task:
```bash
cd workspace/current_tasks
mkdir test-task-$(date +%s)
cd test-task-*
echo '{
  "task_id": "test-analyze-codebase",
  "description": "Analyze codebase for syntax flaws and compare with fixes from Stack Overflow", 
  "agent_type": "auto",
  "status": "available",
  "priority": 3,
  "created_at": '$(date +%s)',
  "created_by": "manual_test",
  "dependencies": []
}' > task.json
```

## 👀 Watching Agents Work

1. **File Explorer**: Open `workspace/current_tasks/` and watch:
   - Task status changes in `task.json` files
   - New subtasks being created
   - Progress logs being updated
   - Results being saved

2. **Terminal Output**: Each agent will show:
   - `🔍 [agent] monitoring workspace...`
   - `🧩 Found complex task: task-xyz`
   - `✅ Completed [operation]`

## 🎯 Expected Flow

1. **Task Breakdown Agent** sees complex task → breaks it into steps
2. **Metacognition Agent** sees planning tasks → creates detailed strategies  
3. **Terminal Agent** sees terminal tasks → executes commands
4. **Search Agent** sees search tasks → performs web searches
5. **File Agent** sees file tasks → reads/writes files

## 🔧 Environment Variables

Agents use these from `.env`:
- `TASK_WORKSPACE_PATH=./workspace`
- `GIT_WORKSPACE_PATH=./workspace`

## ✅ Success Indicators

- Agents stay running (no crashes)
- Task files show status changes (`available` → `claimed` → `in_progress` → `completed`)
- New subtask directories appear
- Progress logs show agent activity
- Results files are created

## 🐛 Debugging

If an agent crashes:
1. Check the terminal output for errors
2. Verify the workspace path is correct
3. Ensure the agent has necessary permissions
4. Check that ADK is properly installed

This simple approach lets you see exactly what each agent is doing and verify the fundamental orchestration works! 