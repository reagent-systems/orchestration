# Search App with A2A Integration

This is an enhanced version of the ADK streaming quickstart that includes A2A (Agent-to-Agent) protocol integration. The app provides a search agent that can use both Google Search and external A2A agents for enhanced capabilities.

## Features

- **ADK Streaming**: Real-time voice and video communication with agents
- **Google Search Integration**: Ground responses with live search results
- **A2A Protocol Support**: Connect to external specialized agents
- **Hybrid Architecture**: Combine local ADK agents with remote A2A agents
- **Fallback Mechanism**: Automatic fallback to external agents when local capabilities are insufficient

## Project Structure

```
search-app/
├── app/
│   ├── env.example              # Environment configuration template
│   ├── a2a_config.py            # A2A configuration and management
│   └── google_search_agent/
│       ├── __init__.py          # Package initialization
│       └── agent.py             # Enhanced agent with A2A integration
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

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

# Integration Configuration
ENABLE_A2A_INTEGRATION=true
A2A_DISCOVERY_INTERVAL=300
MAX_EXTERNAL_AGENTS=10
```

### 4. Model Configuration

Make sure to use a Gemini model that supports the Live API. Update the model in `agent.py` or set the `GEMINI_MODEL` environment variable:

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

4. Open your browser to `http://localhost:8000` and select `enhanced_search_agent`

### Testing Features

#### Text Interaction
Try these prompts:
- "What is the weather in New York?"
- "What is the time in Paris?"
- "Translate 'Hello world' to Spanish"
- "What are the latest news headlines?"

#### Voice and Video
- Click the microphone button for voice input
- Click the camera button for video input
- The agent will respond in real-time with voice/video

## A2A Integration Features

### Automatic Agent Discovery
The app automatically discovers external A2A agents and registers their capabilities.

### Capability-Based Routing
When a task requires specialized capabilities not available through Google Search, the agent can automatically delegate to appropriate external A2A agents.

### Fallback Mechanism
If local execution fails, the system automatically attempts to delegate the task to external A2A agents.

### Example External Agents
The system includes example configurations for:
- **Weather Agent**: Weather forecasts and current conditions
- **Translation Agent**: Text translation between languages
- **News Agent**: Latest news and headlines

## Customization

### Adding New A2A Agents

1. Update the `_discover_agents` method in `a2a_config.py`
2. Add new agent configurations to the discovery list
3. Define capabilities and endpoints

### Modifying Agent Behavior

Edit the `EnhancedSearchAgent` class in `agent.py`:
- Update instructions for different behavior
- Add new tools and capabilities
- Modify the fallback logic

### Configuration Options

Key environment variables:
- `ENABLE_A2A_INTEGRATION`: Enable/disable A2A features
- `A2A_DISCOVERY_INTERVAL`: How often to discover new agents (seconds)
- `MAX_EXTERNAL_AGENTS`: Maximum number of external agents to maintain

## Troubleshooting

### A2A SDK Not Available
If you see "A2A SDK not available" messages:
1. Install the A2A SDK: `pip install a2a-sdk`
2. The app will work without A2A features if the SDK is not available

### Model Issues
If you encounter model-related errors:
1. Verify your API key is correct
2. Ensure you're using a supported Live API model
3. Check the model documentation for latest supported versions

### Streaming Issues
For voice/video streaming problems:
1. Ensure SSL certificate is properly set
2. Check browser permissions for microphone/camera
3. Verify model supports Live API features

## Development

### Adding New Tools
1. Import new tools in `agent.py`
2. Add them to the agent's tools list
3. Update agent instructions if needed

### Extending A2A Integration
1. Modify `A2AIntegrationLayer` class for custom behavior
2. Add new delegation strategies
3. Implement custom agent discovery logic

## Next Steps

- Build custom streaming applications using FastAPI
- Implement more sophisticated A2A agent coordination
- Add monitoring and observability features
- Create production deployment configurations

## Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [A2A Protocol](https://github.com/google-a2a/A2A)
- [Gemini Live API](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming/#supported-models)
- [Streaming Quickstart](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming/) 