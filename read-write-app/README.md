# Read-Write App with A2A Integration

This is an advanced file operations agent system that combines ADK framework with A2A protocol integration. The app provides sophisticated file operations in a git workspace with multi-agent coordination and external agent integration.

## Features

- **File Operations**: Read, write, delete, and list files in a git workspace
- **Git Integration**: Automatic git operations with commit management
- **Multi-Agent Architecture**: Specialized agents for different file operations
- **Workflow Agents**: Sequential, parallel, and loop workflows for complex operations
- **A2A Protocol Support**: Connect to external specialized agents
- **Agent Coordination**: Use AgentTool for explicit agent invocation
- **Streaming Support**: Real-time voice and video communication

## Project Structure

```
read-write-app/
├── app/
│   ├── env.example              # Environment configuration template
│   ├── a2a_config.py            # A2A configuration and management
│   └── file_operations_agent/
│       ├── __init__.py          # Package initialization
│       ├── agent.py             # Main agents and workflows
│       ├── tools.py             # File operation tools
│       └── coordinator.py       # Multi-agent coordinator
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Agent Architecture

### LLM Agents
- **EnhancedFileOperationsAgent**: Main agent with comprehensive file operations
- **File Reader Agent**: Specialized in reading and analyzing files
- **File Writer Agent**: Specialized in writing and creating files
- **Git Manager Agent**: Specialized in git operations and version control

### Workflow Agents
- **FileAnalysisWorkflow**: Sequential workflow for file analysis
- **FileCreationWorkflow**: Sequential workflow for file creation
- **ParallelFileOperations**: Parallel workflow for multiple operations
- **GitManagementLoop**: Loop workflow for continuous git management

### A2A Integration
- **External Agent Discovery**: Automatic discovery of external A2A agents
- **Capability-Based Routing**: Route tasks to appropriate external agents
- **Fallback Mechanism**: Automatic fallback to external agents when needed

## Setup Instructions

### 1. Environment Setup

Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate (each new terminal)
# macOS/Linux: source .venv/bin/activate
# Windows CMD: .venv\Scripts\activate.bat
# Windows PowerShell: .venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configuration

Copy the environment template and configure your settings:

```bash
cd app
cp env.example .env
```

Edit `.env` with your configuration:

```bash
# ADK Configuration
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_actual_api_key_here

# A2A Configuration
A2A_HOST=localhost
A2A_PORT=8080
A2A_AUTH_TOKEN=your_a2a_auth_token_here

# Git Workspace Configuration
GIT_WORKSPACE_PATH=./workspace
GIT_REPO_URL=your_git_repo_url_here
GIT_BRANCH=main
GIT_USER_NAME=Agent User
GIT_USER_EMAIL=agent@example.com

# File Operations Configuration
ENABLE_GIT_OPERATIONS=true
AUTO_COMMIT=true
COMMIT_MESSAGE_PREFIX=[Agent]
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_EXTENSIONS=.txt,.md,.py,.js,.json,.yaml,.yml,.html,.css,.js

# Integration Configuration
ENABLE_A2A_INTEGRATION=true
A2A_DISCOVERY_INTERVAL=300
MAX_EXTERNAL_AGENTS=10

# Agent Coordination
ENABLE_MULTI_AGENT=true
COORDINATOR_AGENT_NAME=file_coordinator
WORKER_AGENT_NAMES=file_reader,file_writer,git_manager
```

### 4. Model Configuration

Make sure to use a Gemini model that supports the Live API:

```bash
# Supported models for voice/video streaming
# - gemini-2.0-flash-live-001
# - gemini-2.0-flash-live-preview-04-09
# Check: https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming/#supported-models
```

## Running the Application

### Using ADK Web Interface

1. Navigate to the app directory:
```bash
cd app
```

2. Set SSL certificate (required for voice/video):
```bash
export SSL_CERT_FILE=$(python -m certifi)
```

3. Launch the development UI:
```bash
adk web
```

4. Open your browser to `http://localhost:8000` and select `enhanced_file_operations_agent`

### Testing Features

#### File Operations
Try these prompts:
- "List all files in the workspace"
- "Read the content of README.md"
- "Create a new file called test.txt with some content"
- "Delete the file test.txt"
- "Create a directory called docs"

#### Git Operations
- "Show the git status of the workspace"
- "Commit all changes with message 'Update files'"
- "What's the current git branch?"

#### Multi-Agent Coordination
- "Analyze all Python files in the workspace"
- "Create a comprehensive documentation structure"
- "Review and organize the workspace files"

#### Voice and Video
- Click the microphone button for voice input
- Click the camera button for video input
- The agent will respond in real-time with voice/video

## Agent Coordination Examples

### Using AgentTool for Explicit Invocation

The system supports explicit agent invocation using AgentTool:

```python
# Example: Invoke file_reader agent
result = await file_reader_agent.execute("Read and analyze the main.py file")

# Example: Invoke file_writer agent
result = await file_writer_agent.execute("Create a new configuration file")

# Example: Invoke git_manager agent
result = await git_manager_agent.execute("Commit all changes with message 'Update'")
```

### Workflow Examples

#### Sequential Workflow
```python
# File analysis workflow: read -> analyze -> report
result = await file_analysis_workflow.execute("Analyze all files in the project")
```

#### Parallel Workflow
```python
# Parallel operations: read, write, and git management simultaneously
result = await parallel_file_operations.execute("Process multiple files")
```

#### Loop Workflow
```python
# Continuous git management
result = await git_management_loop.execute("Monitor and commit changes")
```

## A2A Integration Features

### External Agent Capabilities
The system can connect to external A2A agents with capabilities like:
- **Code Analysis**: Syntax checking, code review, quality analysis
- **Document Processing**: Text extraction, format conversion
- **Image Processing**: Image analysis, conversion, processing
- **Data Analysis**: Statistical analysis, data visualization
- **Backup Management**: File synchronization, version control

### Automatic Discovery
- Discovers external A2A agents automatically
- Registers agent capabilities and endpoints
- Routes tasks to appropriate external agents

### Fallback Mechanism
- Tries local capabilities first
- Falls back to external A2A agents if local capabilities are insufficient
- Provides comprehensive error handling

## Customization

### Adding New File Operations
1. Add new tools to `tools.py`
2. Update agent instructions in `coordinator.py`
3. Create new workflow agents in `agent.py`

### Extending A2A Integration
1. Modify `A2AIntegrationLayer` class for custom behavior
2. Add new external agent capabilities
3. Implement custom delegation strategies

### Creating Custom Workflows
1. Define new workflow classes inheriting from `SequentialAgent`, `ParallelAgent`, or `LoopAgent`
2. Configure agent sequences and conditions
3. Add to the main agent system

## Configuration Options

### File Operations
- `MAX_FILE_SIZE_MB`: Maximum file size for operations
- `ALLOWED_FILE_EXTENSIONS`: File types allowed for operations
- `AUTO_COMMIT`: Automatic git commits after file operations

### Git Configuration
- `GIT_WORKSPACE_PATH`: Path to the git workspace
- `GIT_REPO_URL`: Remote repository URL
- `COMMIT_MESSAGE_PREFIX`: Prefix for commit messages

### Agent Coordination
- `ENABLE_MULTI_AGENT`: Enable multi-agent coordination
- `COORDINATOR_AGENT_NAME`: Name of the main coordinator agent
- `WORKER_AGENT_NAMES`: Names of worker agents

## Troubleshooting

### Git Issues
- Ensure git is properly configured
- Check repository permissions
- Verify git user configuration

### File Operation Issues
- Check file permissions
- Verify file size limits
- Ensure allowed file extensions

### A2A Integration Issues
- Verify A2A SDK installation
- Check network connectivity
- Validate agent discovery configuration

## Development

### Adding New Tools
1. Create new `@FunctionTool` decorated methods in `tools.py`
2. Add tools to appropriate agents in `coordinator.py`
3. Update agent instructions to include new capabilities

### Testing Workflows
1. Test individual agents first
2. Test workflow combinations
3. Validate A2A integration

### Performance Optimization
1. Monitor file operation performance
2. Optimize git operations
3. Tune agent coordination

## Next Steps

- Build custom streaming applications using FastAPI
- Implement more sophisticated A2A agent coordination
- Add monitoring and observability features
- Create production deployment configurations
- Develop specialized external agents

## Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [LLM Agents](https://google.github.io/adk-docs/agents/llm-agents/)
- [Workflow Agents](https://google.github.io/adk-docs/agents/workflow-agents/)
- [Multi-Agent Systems](https://google.github.io/adk-docs/agents/multi-agents/)
- [A2A Protocol](https://github.com/google-a2a/A2A)
- [Streaming Quickstart](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming/) 