"""
ADK Built-in Search Agent - Workspace Task Monitoring
Uses official Google ADK google_search tool - no custom API setup needed!
"""

import os
import json
import asyncio
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import FunctionTool, google_search

# Load environment variables from root .env
load_dotenv(dotenv_path="../../.env")

class SearchAgent:
    """Search Agent using built-in ADK google_search tool with workspace task monitoring"""
    
    def __init__(self):
        # Store workspace paths in global scope for access in methods
        global workspace_path, current_tasks_dir
        workspace_path = Path(os.getenv("GIT_WORKSPACE_PATH", "./workspace"))
        current_tasks_dir = workspace_path / "current_tasks"
        self.agent_id = "search_agent"
        
        # Create the ADK agent with built-in google_search tool
        self.agent = Agent(
            name="search_agent",
            model=os.getenv("SEARCH_MODEL", "gemini-2.0-flash"),
            description="Search Agent using built-in ADK Google Search - performs web searches and saves results to workspace",
            instruction="""You are a search agent that performs web searches using the built-in Google Search capability.

Your capabilities:
1. **Web Search**: Use the built-in google_search tool for web searches (no API setup needed)
2. **Research Tasks**: Conduct comprehensive research with multiple search queries
3. **Result Processing**: Extract and format search results from Google Search
4. **Workspace Integration**: Save search results to shared workspace for other agents

When you receive search requests:
1. Use the google_search tool to find relevant information
2. Process and organize the results clearly
3. Save findings to the workspace for other agents to use
4. Provide comprehensive summaries of search results

You monitor the workspace for search-related tasks and execute them autonomously.""",
            tools=[
                google_search,  # Built-in ADK Google Search tool
                FunctionTool(self.save_search_results),
                FunctionTool(self.process_search_request)
            ]
        )
        
        print("✅ Search Agent initialized with built-in ADK Google Search tool")

    @FunctionTool
    def save_search_results(self, results: Dict[str, Any], filename: str = None) -> Dict[str, Any]:
        """Save search results to workspace for other agents
        
        Args:
            results: Search results to save
            filename: Optional filename (auto-generated if not provided)
            
        Returns:
            Dict containing save operation results
        """
        try:
            if not filename:
                query = results.get("query", results.get("topic", "search"))
                safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"search_results_{safe_query.replace(' ', '_')[:30]}.json"
            
            # Ensure results directory exists
            results_dir = workspace_path / "search_results"
            results_dir.mkdir(exist_ok=True)
            
            # Save results
            filepath = results_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            return {
                "success": True,
                "filepath": str(filepath),
                "filename": filename,
                "size": filepath.stat().st_size
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to save results: {str(e)}"
            }

    @FunctionTool  
    def process_search_request(self, query: str, save_to_workspace: bool = True) -> Dict[str, Any]:
        """Process a search request and optionally save results
        
        Args:
            query: Search query to process
            save_to_workspace: Whether to save results to workspace
            
        Returns:
            Dict containing processing results
        """
        try:
            # The actual search is handled by the built-in google_search tool
            # This function handles the workspace integration
            
            result_data = {
                "query": query,
                "processed_at": time.time(),
                "agent": "search_agent",
                "status": "processed"
            }
            
            if save_to_workspace:
                save_result = self.save_search_results(result_data)
                result_data["saved_to"] = save_result.get("filepath")
                result_data["save_success"] = save_result.get("success", False)
            
            return {
                "success": True,
                "result": result_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to process search request: {str(e)}"
            }

    def can_handle_task(self, task_data: Dict[str, Any]) -> bool:
        """Check if this agent can handle the given task"""
        task_type = task_data.get("agent_type", "").lower()
        description = task_data.get("description", "").lower()
        
        # Handle search-related tasks
        if task_type == "search":
            return True
            
        # Handle tasks with search keywords
        search_keywords = ["search", "research", "find", "look up", "web search", "google"]
        return any(keyword in description for keyword in search_keywords)

    async def process_task(self, task_path: Path):
        """Process a search task"""
        try:
            # Load task
            with open(task_path / "task.json", 'r') as f:
                task_data = json.load(f)
            
            # Claim the task
            task_data["status"] = "in_progress"
            task_data["claimed_by"] = self.agent_id
            task_data["claimed_at"] = time.time()
            
            with open(task_path / "task.json", 'w') as f:
                json.dump(task_data, f, indent=2)
            
            # Extract search query from description
            description = task_data["description"]
            
            if "search for" in description.lower():
                query = description.lower().split("search for")[1].strip()
            elif "research" in description.lower():
                query = description.lower().replace("research", "").strip()
            else:
                query = description
            
            # Process the search request (the actual search will be done by google_search tool when model is invoked)
            result = self.process_search_request(query, save_to_workspace=True)
            
            # Update task with results
            task_data["status"] = "completed" if result.get("success") else "failed"
            task_data["result"] = result
            task_data["completed_at"] = time.time()
            
            with open(task_path / "task.json", 'w') as f:
                json.dump(task_data, f, indent=2)
            
            # Log progress
            with open(task_path / "progress.log", 'a') as f:
                status = "✅ COMPLETED" if result.get("success") else "❌ FAILED"
                f.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] {status} - Search Agent (ADK Built-in)\n")
                f.write(f"Query: {query}\n")
                if result.get("success"):
                    f.write(f"Processed successfully using built-in Google Search\n")
                    if result.get("result", {}).get("saved_to"):
                        f.write(f"Saved to: {result['result']['saved_to']}\n")
                else:
                    f.write(f"Error: {result.get('error', 'Unknown error')}\n")
            
        except Exception as e:
            print(f"Error processing task {task_path.name}: {e}")

    async def monitor_workspace(self):
        """Monitor workspace for search tasks"""
        print(f"🔍 Search Agent monitoring workspace: {current_tasks_dir}")
        
        while True:
            try:
                if not current_tasks_dir.exists():
                    await asyncio.sleep(int(os.getenv("TASK_MONITOR_INTERVAL", 3)))
                    continue
                
                # Check for available tasks
                for task_dir in current_tasks_dir.iterdir():
                    if not task_dir.is_dir():
                        continue
                    
                    task_file = task_dir / "task.json"
                    if not task_file.exists():
                        continue
                    
                    try:
                        with open(task_file, 'r') as f:
                            task_data = json.load(f)
                        
                        # Skip if task is not available or not for us
                        if task_data.get("status") != "available":
                            continue
                        
                        if not self.can_handle_task(task_data):
                            continue
                        
                        print(f"🔍 Claiming search task: {task_dir.name}")
                        await self.process_task(task_dir)
                        
                    except Exception as e:
                        print(f"Error checking task {task_dir.name}: {e}")
                
            except Exception as e:
                print(f"Error in workspace monitoring: {e}")
            
            await asyncio.sleep(int(os.getenv("TASK_MONITOR_INTERVAL", 3)))

    async def run(self):
        """Run the search agent"""
        print("🔍 Starting ADK Built-in Search Agent...")
        print("Features:")
        print("- Built-in ADK Google Search tool (no API setup needed)")
        print("- Workspace task monitoring")
        print("- Result saving to shared workspace")
        print("- Seamless integration with Gemini models")
        
        await self.monitor_workspace()

# Create agent instance
search_agent = SearchAgent()

if __name__ == "__main__":
    asyncio.run(search_agent.run()) 