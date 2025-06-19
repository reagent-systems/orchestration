"""
Autonomous Google Search Agent
Self-contained agent that provides web search capabilities and can discover/invoke other agents via A2A
All agents operate in the same shared git workspace
"""

import os
import asyncio
from typing import Optional, Dict, Any, List
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

class AutonomousSearchAgent(Agent):
    """Autonomous search agent with web search capabilities and A2A agent discovery"""
    
    def __init__(self, name: str = "autonomous_search_agent", model: str = None):
        # Define our own tools
        tools = [
            FunctionTool(self.web_search),
            FunctionTool(self.research_topic),
            FunctionTool(self.discover_agents),
            FunctionTool(self.invoke_agent),
            FunctionTool(self.gather_comprehensive_info)
        ]
        
        super().__init__(
            name=name,
            model=model or os.getenv("SEARCH_MODEL", "gemini-2.0-flash-live-001"),
            description="Autonomous Search Agent with web search and A2A agent discovery",
            instruction="""You are an autonomous search agent specialized in web search and information gathering.

Your core abilities:
1. **Web Search**: Perform comprehensive web searches and information gathering
2. **Research**: Conduct deep research on topics using multiple search strategies
3. **Agent Discovery**: Use A2A protocol to discover other available agents
4. **Agent Invocation**: Call other agents when you need their capabilities (file ops, analysis, etc.)
5. **Information Synthesis**: Combine and analyze information from multiple sources

When you receive a request:
1. **Analyze** what information is needed
2. **Search** the web for relevant information
3. **Discover** other agents if you need additional capabilities
4. **Invoke** other agents for tasks like file operations or analysis in shared workspace
5. **Synthesize** and present comprehensive results

Available agent discovery via A2A:
- File operation agents for saving research results to shared workspace
- Metacognition agents for analysis and insights
- Other search agents for collaboration

You work autonomously in the shared git workspace - no central orchestrator controls you. You decide how to collaborate with other agents based on the information gathering requirements.""",
            tools=tools
        )
        
        # A2A configuration
        self.a2a_enabled = os.getenv("ENABLE_A2A_INTEGRATION", "true").lower() == "true"
        self.discovered_agents = {}
        # Shared workspace configuration
        self.shared_workspace = os.getenv("GIT_WORKSPACE_PATH", "./workspace")
        
    @FunctionTool
    async def web_search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Perform a web search for the given query
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            Dict containing search results
        """
        try:
            # Simulate web search (in real implementation, this would use actual search APIs)
            results = [
                {
                    "title": f"Search result {i} for: {query}",
                    "url": f"https://example.com/result-{i}",
                    "snippet": f"This is a simulated search result snippet for query '{query}'. Result number {i}.",
                    "relevance_score": 0.9 - (i * 0.1)
                }
                for i in range(1, min(max_results + 1, 6))
            ]
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "total_results": len(results)
            }
            
        except Exception as e:
            return {"error": f"Web search failed: {str(e)}"}
    
    @FunctionTool
    async def research_topic(self, topic: str, depth: str = "medium") -> Dict[str, Any]:
        """Conduct comprehensive research on a topic
        
        Args:
            topic: Topic to research
            depth: Research depth (shallow, medium, deep)
            
        Returns:
            Dict containing research results
        """
        try:
            # Determine search strategy based on depth
            if depth == "shallow":
                queries = [topic]
            elif depth == "medium":
                queries = [topic, f"{topic} overview", f"{topic} examples"]
            else:  # deep
                queries = [topic, f"{topic} overview", f"{topic} examples", f"{topic} best practices", f"{topic} latest developments"]
            
            all_results = []
            for query in queries:
                search_result = await self.web_search(query, max_results=5)
                if search_result.get("success"):
                    all_results.extend(search_result["results"])
            
            # Synthesize findings
            synthesis = {
                "topic": topic,
                "research_depth": depth,
                "total_sources": len(all_results),
                "key_findings": [
                    f"Finding 1: {topic} is an important subject with multiple aspects",
                    f"Finding 2: Research shows various approaches to {topic}",
                    f"Finding 3: Current trends in {topic} indicate continued development"
                ],
                "sources": all_results
            }
            
            return {
                "success": True,
                "research": synthesis
            }
            
        except Exception as e:
            return {"error": f"Research failed: {str(e)}"}
    
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
                "file_operations_agent": {
                    "endpoint": os.getenv("READ_WRITE_AGENT_ENDPOINT", "http://localhost:8002"),
                    "capabilities": ["file_read", "file_write", "git_operations", "workspace_management"],
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
    async def gather_comprehensive_info(self, request: str, save_results: bool = False) -> Dict[str, Any]:
        """Gather comprehensive information on a topic, optionally saving results
        
        Args:
            request: Information gathering request
            save_results: Whether to save results using file operations agent
            
        Returns:
            Dict containing comprehensive information
        """
        try:
            # Step 1: Research the topic
            research_result = await self.research_topic(request, depth="deep")
            
            if not research_result.get("success"):
                return {"error": f"Research failed: {research_result.get('error')}"}
            
            # Step 2: If saving is requested, discover file operations agent
            if save_results:
                discovery_result = await self.discover_agents("file_write")
                
                if discovery_result.get("success") and "file_operations_agent" in discovery_result["agents"]:
                    # Step 3: Save the research results
                    save_result = await self.invoke_agent(
                        "file_operations_agent",
                        "save_research",
                        {
                            "filename": f"research_{request.replace(' ', '_')}.md",
                            "content": research_result["research"],
                            "format": "markdown"
                        }
                    )
                    
                    return {
                        "success": True,
                        "request": request,
                        "research": research_result["research"],
                        "saved": save_result.get("success", False),
                        "save_location": save_result.get("response", "Not saved")
                    }
            
            return {
                "success": True,
                "request": request,
                "research": research_result["research"],
                "saved": False
            }
            
        except Exception as e:
            return {"error": f"Information gathering failed: {str(e)}"}

# Create the autonomous agent instance
autonomous_search_agent = AutonomousSearchAgent()

if __name__ == "__main__":
    import asyncio
    
    async def main():
        """Main entry point for the autonomous search agent"""
        print("Starting Autonomous Search Agent...")
        print("Autonomous Search Agent is ready!")
        print("This agent can:")
        print("- Perform web searches and research")
        print("- Discover other agents via A2A protocol")
        print("- Invoke other agents for additional capabilities")
        print("- Gather and synthesize comprehensive information")
        
        # Keep the agent running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down...")
    
    asyncio.run(main()) 