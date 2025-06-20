# Current Tasks

This directory contains **active tasks** being worked on by agents.

## File Organization

- Each task gets its own subdirectory: `current_tasks/[task-id]/`
- Task metadata in `task.json`
- Working files in the task subdirectory
- Progress updates via git commits

## Task Structure

```
current_tasks/
├── task-001-web-research/
│   ├── task.json           # Task metadata and status
│   ├── search_results.md   # Agent work products
│   ├── analysis.md         # Analysis from metacognition agent
│   └── progress.log        # Detailed progress log
└── task-002-file-ops/
    ├── task.json
    ├── modified_files.list
    └── operation_log.md
```

## Task Metadata Format (task.json)

```json
{
  "task_id": "task-001-web-research",
  "title": "Research Topic X",
  "description": "Comprehensive research on topic X",
  "created_by": "metacognition_agent",
  "assigned_agents": ["search_agent", "metacognition_agent"],
  "status": "in_progress",
  "progress": 0.65,
  "created_at": "2025-06-18T22:00:00Z",
  "updated_at": "2025-06-18T22:30:00Z",
  "dependencies": [],
  "blockers": [],
  "next_actions": ["finalize_analysis", "generate_summary"]
}
```

## Git Workflow

- **Branch per task**: `git checkout -b task/web-research`
- **Progress commits**: `[SEARCH] Found 10 relevant sources - Progress: 40%`
- **Collaboration**: Multiple agents commit to same task branch
- **Completion**: Merge to main and move to `completed_tasks/` 