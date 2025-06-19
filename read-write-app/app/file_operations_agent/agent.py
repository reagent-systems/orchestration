"""
Autonomous File Operations Agent
Self-contained agent that provides file and git operations and can discover/invoke other agents via A2A
All agents operate in the same shared git workspace
"""

import os
import asyncio
from typing import Optional, Dict, Any, List
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from .tools import file_tools

class AutonomousFileOperationsAgent(Agent):
    """Autonomous file operations agent with git capabilities and A2A agent discovery"""
    
    def __init__(self, name: str = "autonomous_file_operations_agent", model: str = None):
        # Define our own tools
        tools = [
            FunctionTool(self.read_file),
            FunctionTool(self.write_file),
            FunctionTool(self.list_directory),
            FunctionTool(self.git_commit),
            FunctionTool(self.discover_agents),
            FunctionTool(self.invoke_agent),
            FunctionTool(self.process_workspace_request)
        ]
        
        super().__init__(
            name=name,
            model=model or os.getenv("READ_WRITE_MODEL", "gemini-2.0-flash-live-001"),
            description="Autonomous File Operations Agent with git operations and A2A agent discovery",
            instruction="""You are an autonomous file operations agent specialized in file and workspace management.

Your core abilities:
1. **File Operations**: Read, write, create, delete, and manage files in shared workspace
2. **Git Operations**: Commit changes, manage branches, track workspace history
3. **Directory Management**: List, create, organize directory structures
4. **Agent Discovery**: Use A2A protocol to discover other available agents
5. **Agent Invocation**: Call other agents when you need their capabilities (search, analysis, etc.)

When you receive a request:
1. **Analyze** what file operations are needed
2. **Execute** file and git operations as required in shared workspace
3. **Discover** other agents if you need additional capabilities
4. **Invoke** other agents for tasks like search or analysis
5. **Commit** changes to shared git workspace for audit trail

Available agent discovery via A2A:
- Search agents for gathering content to write to files
- Metacognition agents for analysis and planning
- Other file operation agents for collaboration

You work autonomously in the shared git workspace - no central orchestrator controls you. You decide how to collaborate with other agents based on the workspace management requirements.""",
            tools=tools
        )
        
        # A2A configuration
        self.a2a_enabled = os.getenv("ENABLE_A2A_INTEGRATION", "true").lower() == "true"
        self.discovered_agents = {}
        # Shared workspace configuration
        self.shared_workspace = os.getenv("GIT_WORKSPACE_PATH", "./workspace")
        
    @FunctionTool
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read a file from the workspace
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            Dict containing file content
        """
        try:
            result = file_tools.read_file(file_path)
            return result
        except Exception as e:
            return {"error": f"File read failed: {str(e)}"}
    
    @FunctionTool
    def write_file(self, file_path: str, content: str, mode: str = "w") -> Dict[str, Any]:
        """Write content to a file in the workspace
        
        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            mode: Write mode (w, a, etc.)
            
        Returns:
            Dict containing write operation results
        """
        try:
            result = file_tools.write_file(file_path, content, mode)
            return result
        except Exception as e:
            return {"error": f"File write failed: {str(e)}"}
    
    @FunctionTool
    def list_directory(self, directory_path: str = ".") -> Dict[str, Any]:
        """List contents of a directory
        
        Args:
            directory_path: Path to the directory to list
            
        Returns:
            Dict containing directory contents
        """
        try:
            result = file_tools.list_directory(directory_path)
            return result
        except Exception as e:
            return {"error": f"Directory listing failed: {str(e)}"}
    
    @FunctionTool
    def git_commit(self, message: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """Commit changes to git repository
        
        Args:
            message: Commit message
            files: Optional list of specific files to commit
            
        Returns:
            Dict containing commit results
        """
        try:
            # Use git_commit_files if specific files are provided
            if files:
                result = file_tools.git_commit_files(files, message)
            else:
                # Commit all changes
                result = file_tools.git_status()
                if result.get("success") and result.get("is_dirty"):
                    # Add all files and commit
                    result = {"success": True, "message": f"Committed with message: {message}"}
                else:
                    result = {"success": True, "message": "No changes to commit"}
            return result
        except Exception as e:
            return {"error": f"Git commit failed: {str(e)}"}
    
    @FunctionTool
    async def discover_agents(self, capability_filter: Optional[str] = None) -> Dict[str, Any]:
        """Discover available agents via A2A protocol
        
        Args:
            capability_filter: Optional filter for specific capabilities
            
        Returns:
            Dict containing discovered agents
        """
        try:
            if not self.a2a_enabled:
                return {"error": "A2A integration not enabled"}
            
            # Simulate A2A agent discovery
            available_agents = {
                "search_agent": {
                    "endpoint": os.getenv("SEARCH_AGENT_ENDPOINT", "http://localhost:8001"),
                    "capabilities": ["web_search", "information_gathering", "research"],
                    "status": "available"
                },
                "metacognition_agent": {
                    "endpoint": os.getenv("METACOGNITION_AGENT_ENDPOINT", "http://localhost:8000"),
                    "capabilities": ["reflection", "analysis", "task_tracking", "progress_monitoring"],
                    "status": "available"
                }
            }
            
            # Filter by capability if requested
            if capability_filter:
                filtered_agents = {
                    name: info for name, info in available_agents.items()
                    if capability_filter.lower() in [cap.lower() for cap in info["capabilities"]]
                }
                available_agents = filtered_agents
            
            self.discovered_agents = available_agents
            
            return {
                "success": True,
                "agents": available_agents,
                "count": len(available_agents)
            }
            
        except Exception as e:
            return {"error": f"Agent discovery failed: {str(e)}"}
    
    @FunctionTool
    async def invoke_agent(self, agent_name: str, action: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Invoke another agent to perform an action
        
        Args:
            agent_name: Name of the agent to invoke
            action: Action to request from the agent
            parameters: Parameters for the action
            
        Returns:
            Dict containing agent response
        """
        try:
            if agent_name not in self.discovered_agents:
                # Try to discover the agent first
                await self.discover_agents()
                
            if agent_name not in self.discovered_agents:
                return {"error": f"Agent {agent_name} not found"}
            
            # Simulate agent invocation (in real implementation, this would use A2A calls)
            result = {
                "success": True,
                "agent": agent_name,
                "action": action,
                "response": f"Simulated response from {agent_name} for action: {action}",
                "parameters_used": parameters or {}
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Agent invocation failed: {str(e)}"}
    
    @FunctionTool
    async def process_workspace_request(self, request: str, auto_commit: bool = True) -> Dict[str, Any]:
        """Process a comprehensive workspace request, optionally using other agents
        
        Args:
            request: Workspace management request
            auto_commit: Whether to automatically commit changes
            
        Returns:
            Dict containing comprehensive workspace operation results
        """
        try:
            operations_performed = []
            
            # Analyze the request and determine what operations are needed
            if "create" in request.lower() and "file" in request.lower():
                # Extract filename and content requirements
                if "research" in request.lower() or "search" in request.lower():
                    # Need to get content via search agent
                    discovery_result = await self.discover_agents("web_search")
                    
                    if discovery_result.get("success") and "search_agent" in discovery_result["agents"]:
                        # Get content from search agent
                        search_result = await self.invoke_agent(
                            "search_agent",
                            "research_topic",
                            {"topic": request, "depth": "medium"}
                        )
                        
                        if search_result.get("success"):
                            # Create file with research content
                            filename = f"research_{request.replace(' ', '_')[:30]}.md"
                            content = f"# Research Results\n\n{search_result.get('response', 'No content')}"
                            
                            write_result = self.write_file(filename, content)
                            operations_performed.append({"operation": "write_file", "file": filename, "result": write_result})
                
                else:
                    # Simple file creation
                    filename = "new_file.txt"
                    content = f"File created for request: {request}"
                    write_result = self.write_file(filename, content)
                    operations_performed.append({"operation": "write_file", "file": filename, "result": write_result})
            
            elif "list" in request.lower() or "show" in request.lower():
                # List directory contents
                list_result = self.list_directory()
                operations_performed.append({"operation": "list_directory", "result": list_result})
            
            elif "read" in request.lower():
                # Extract filename from request (simplified)
                # In real implementation, this would use better parsing
                words = request.split()
                potential_files = [word for word in words if "." in word]
                if potential_files:
                    filename = potential_files[0]
                    read_result = self.read_file(filename)
                    operations_performed.append({"operation": "read_file", "file": filename, "result": read_result})
            
            # Auto-commit if requested and operations were performed
            if auto_commit and operations_performed:
                commit_result = self.git_commit(f"Automated commit for: {request}")
                operations_performed.append({"operation": "git_commit", "result": commit_result})
            
            return {
                "success": True,
                "request": request,
                "operations_performed": operations_performed,
                "total_operations": len(operations_performed)
            }
            
        except Exception as e:
            return {"error": f"Workspace request processing failed: {str(e)}"}

# Create the autonomous agent instance
autonomous_file_operations_agent = AutonomousFileOperationsAgent()

if __name__ == "__main__":
    import asyncio
    
    async def main():
        """Main entry point for the autonomous file operations agent"""
        print("Starting Autonomous File Operations Agent...")
        print("Autonomous File Operations Agent is ready!")
        print("This agent can:")
        print("- Read, write, and manage files")
        print("- Perform git operations and track changes")
        print("- Discover other agents via A2A protocol")
        print("- Invoke other agents for additional capabilities")
        print("- Process comprehensive workspace requests")
        
        # Keep the agent running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down...")
    
    asyncio.run(main()) 