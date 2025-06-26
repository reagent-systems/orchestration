"""
Real File Operations Agent - Workspace Task Monitoring
No simulations - performs actual file operations and monitors workspace for file tasks
"""

import os
import json
import asyncio
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
# Load environment variables from root .env
load_dotenv(dotenv_path="../../../.env")

class FileOperationsAgent:
    """Real File Operations Agent with workspace task monitoring"""
    
    def __init__(self):
        # Store workspace paths in global scope for access in methods
        global workspace_path, current_tasks_dir
        workspace_path = Path(os.getenv("GIT_WORKSPACE_PATH", "./workspace"))
        current_tasks_dir = workspace_path / "current_tasks"
        self.agent_id = "file_operations_agent"
        
        # Define tools for the ADK agent
        tools = [
            FunctionTool(self.read_file),
            FunctionTool(self.write_file),
            FunctionTool(self.create_file),
            FunctionTool(self.delete_file),
            FunctionTool(self.list_directory),
            FunctionTool(self.create_directory),
            FunctionTool(self.git_commit),
            FunctionTool(self.process_file_batch)
        ]
        
        self.agent = Agent(
            name="file_operations_agent",
            model=os.getenv("READ_WRITE_MODEL", "gemini-2.0-flash"),
            description="Real File Operations Agent - performs actual file operations and git management",
            instruction="""You are a file operations agent that performs real file and directory operations.

Your capabilities:
1. **File Operations**: Read, write, create, delete files with proper error handling
2. **Directory Management**: Create directories, list contents, organize file structures
3. **Git Operations**: Commit changes, track workspace history with meaningful messages
4. **Batch Processing**: Handle multiple file operations efficiently
5. **Workspace Management**: Maintain clean, organized workspace structure

You monitor the workspace for file-related tasks and execute them autonomously with proper safety checks.""",
            tools=tools
        )
        
    @FunctionTool
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read a file from the workspace
        
        Args:
            file_path: Path to the file to read (relative to workspace)
            
        Returns:
            Dict containing file content and metadata
        """
        try:
            # Resolve path relative to workspace
            if not file_path.startswith('/'):
                full_path = workspace_path / file_path
            else:
                full_path = Path(file_path)
            
            if not full_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            if not full_path.is_file():
                return {
                    "success": False,
                    "error": f"Path is not a file: {file_path}"
                }
            
            # Read file content
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "file_path": file_path,
                "content": content,
                "size": full_path.stat().st_size,
                "modified": full_path.stat().st_mtime
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read file: {str(e)}"
            }
    
    @FunctionTool
    def write_file(self, file_path: str, content: str, mode: str = "w") -> Dict[str, Any]:
        """Write content to a file in the workspace
        
        Args:
            file_path: Path to the file to write (relative to workspace)
            content: Content to write to the file
            mode: Write mode ('w' for write, 'a' for append)
            
        Returns:
            Dict containing write operation results
        """
        try:
            # Resolve path relative to workspace
            if not file_path.startswith('/'):
                full_path = workspace_path / file_path
            else:
                full_path = Path(file_path)
            
            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file content
            with open(full_path, mode, encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "file_path": file_path,
                "bytes_written": len(content.encode('utf-8')),
                "mode": mode,
                "size": full_path.stat().st_size
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to write file: {str(e)}"
            }

    @FunctionTool
    def create_file(self, file_path: str, content: str = "") -> Dict[str, Any]:
        """Create a new file with optional initial content
        
        Args:
            file_path: Path to the new file (relative to workspace)
            content: Optional initial content
            
        Returns:
            Dict containing creation results
        """
        try:
            # Resolve path relative to workspace
            if not file_path.startswith('/'):
                full_path = workspace_path / file_path
            else:
                full_path = Path(file_path)
            
            if full_path.exists():
                return {
                    "success": False,
                    "error": f"File already exists: {file_path}"
                }
            
            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create file with content
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "file_path": file_path,
                "created": True,
                "size": full_path.stat().st_size
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create file: {str(e)}"
            }

    @FunctionTool
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """Delete a file from the workspace
        
        Args:
            file_path: Path to the file to delete (relative to workspace)
            
        Returns:
            Dict containing deletion results
        """
        try:
            # Resolve path relative to workspace
            if not file_path.startswith('/'):
                full_path = workspace_path / file_path
            else:
                full_path = Path(file_path)
            
            if not full_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            if not full_path.is_file():
                return {
                    "success": False,
                    "error": f"Path is not a file: {file_path}"
                }
            
            # Delete the file
            full_path.unlink()
            
            return {
                "success": True,
                "file_path": file_path,
                "deleted": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete file: {str(e)}"
            }
    
    @FunctionTool
    def list_directory(self, directory_path: str = ".") -> Dict[str, Any]:
        """List contents of a directory
        
        Args:
            directory_path: Path to the directory to list (relative to workspace)
            
        Returns:
            Dict containing directory contents
        """
        try:
            # Resolve path relative to workspace
            if directory_path == "." or directory_path == "":
                full_path = workspace_path
            elif not directory_path.startswith('/'):
                full_path = workspace_path / directory_path
            else:
                full_path = Path(directory_path)
            
            if not full_path.exists():
                return {
                    "success": False,
                    "error": f"Directory not found: {directory_path}"
                }
            
            if not full_path.is_dir():
                return {
                    "success": False,
                    "error": f"Path is not a directory: {directory_path}"
                }
            
            # List directory contents
            contents = []
            for item in full_path.iterdir():
                contents.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                    "modified": item.stat().st_mtime
                })
            
            return {
                "success": True,
                "directory_path": directory_path,
                "contents": sorted(contents, key=lambda x: (x["type"], x["name"])),
                "total_items": len(contents)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list directory: {str(e)}"
            }

    @FunctionTool
    def create_directory(self, directory_path: str) -> Dict[str, Any]:
        """Create a new directory
        
        Args:
            directory_path: Path to the directory to create (relative to workspace)
            
        Returns:
            Dict containing creation results
        """
        try:
            # Resolve path relative to workspace
            if not directory_path.startswith('/'):
                full_path = workspace_path / directory_path
            else:
                full_path = Path(directory_path)
            
            if full_path.exists():
                return {
                    "success": False,
                    "error": f"Directory already exists: {directory_path}"
                }
            
            # Create directory
            full_path.mkdir(parents=True, exist_ok=True)
            
            return {
                "success": True,
                "directory_path": directory_path,
                "created": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create directory: {str(e)}"
            }
    
    @FunctionTool
    def git_commit(self, message: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """Commit changes to git repository
        
        Args:
            message: Commit message
            files: Optional list of specific files to commit (relative to workspace)
            
        Returns:
            Dict containing commit results
        """
        try:
            import subprocess
            import os
            
            # Change to workspace directory
            original_cwd = os.getcwd()
            os.chdir(workspace_path)
            
            try:
                # Add files to git
                if files:
                    for file_path in files:
                        subprocess.run(['git', 'add', file_path], check=True)
                else:
                    subprocess.run(['git', 'add', '.'], check=True)
                
                # Commit changes
                result = subprocess.run(['git', 'commit', '-m', message], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "message": f"Committed: {message}",
                        "output": result.stdout
                    }
                else:
                    return {
                        "success": False,
                        "error": result.stderr or "Git commit failed"
                    }
                    
            finally:
                # Restore original directory
                os.chdir(original_cwd)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Git commit failed: {str(e)}"
            }
    
    @FunctionTool
    def process_file_batch(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process multiple file operations in batch
        
        Args:
            operations: List of operations, each with 'type' and relevant parameters
            
        Returns:
            Dict containing batch operation results
        """
        results = []
        successful = 0
        failed = 0
        
        for i, op in enumerate(operations):
            op_type = op.get("type")
            
            try:
                if op_type == "write":
                    result = self.write_file(op["file_path"], op["content"], op.get("mode", "w"))
                elif op_type == "read":
                    result = self.read_file(op["file_path"])
                elif op_type == "create":
                    result = self.create_file(op["file_path"], op.get("content", ""))
                elif op_type == "delete":
                    result = self.delete_file(op["file_path"])
                elif op_type == "create_dir":
                    result = self.create_directory(op["directory_path"])
                else:
                    result = {"success": False, "error": f"Unknown operation type: {op_type}"}
                
                results.append({"operation": i, "type": op_type, "result": result})
                
                if result.get("success"):
                    successful += 1
                else:
                    failed += 1
                    
            except Exception as e:
                results.append({
                    "operation": i, 
                    "type": op_type, 
                    "result": {"success": False, "error": str(e)}
                })
                failed += 1
            
            return {
            "success": failed == 0,
            "total_operations": len(operations),
            "successful": successful,
            "failed": failed,
            "results": results
        }

    def can_handle_task(self, task_data: Dict[str, Any]) -> bool:
        """Check if this agent can handle the given task"""
        task_type = task_data.get("agent_type", "").lower()
        description = task_data.get("description", "").lower()
        
        # Handle file-related tasks
        if task_type == "file":
            return True
            
        # Handle tasks with file operation keywords
        file_keywords = ["file", "write", "read", "create", "delete", "directory", "folder", "save"]
        return any(keyword in description for keyword in file_keywords)

    async def process_task(self, task_path: Path):
        """Process a file operations task"""
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
            
            # Execute the task based on description
            description = task_data["description"]
            result = None
            
            if "write" in description.lower() or "create" in description.lower():
                # Extract file path and content from description
                # Simple parsing - in production would use better NLP
                words = description.split()
                file_path = None
                content = description  # Default content
                
                for word in words:
                    if "." in word and "/" not in word:  # Simple file detection
                        file_path = word
                        break
                
                if not file_path:
                    file_path = "task_output.txt"
                
                result = self.write_file(file_path, f"Output from task: {description}")
                
            elif "read" in description.lower():
                # Extract file path from description
                words = description.split()
                file_path = None
                
                for word in words:
                    if "." in word:
                        file_path = word
                        break
                
                if file_path:
                    result = self.read_file(file_path)
                else:
                    result = {"success": False, "error": "No file path specified"}
                    
            elif "list" in description.lower() or "directory" in description.lower():
                # List directory contents
                result = self.list_directory()
                
            else:
                # Generic file operation
                result = {"success": False, "error": "Could not determine file operation"}
            
            # Auto-commit if successful
            if result and result.get("success"):
                commit_msg = f"File operation completed: {description[:50]}..."
                commit_result = self.git_commit(commit_msg)
                result["committed"] = commit_result.get("success", False)
            
            # Update task with results
            task_data["status"] = "completed" if result and result.get("success") else "failed"
            task_data["result"] = result
            task_data["completed_at"] = time.time()
            
            with open(task_path / "task.json", 'w') as f:
                json.dump(task_data, f, indent=2)
            
            # Log progress
            with open(task_path / "progress.log", 'a') as f:
                status = "✅ COMPLETED" if result and result.get("success") else "❌ FAILED"
                f.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] {status} - File Operations Agent\n")
                f.write(f"Operation: {description}\n")
                if result and result.get("success"):
                    f.write(f"Result: Operation successful\n")
                    if result.get("committed"):
                        f.write(f"Changes committed to git\n")
                else:
                    f.write(f"Error: {result.get('error', 'Unknown error') if result else 'No result'}\n")
            
        except Exception as e:
            print(f"Error processing task {task_path.name}: {e}")

    async def monitor_workspace(self):
        """Monitor workspace for file operation tasks"""
        print(f"📁 File Operations Agent monitoring workspace: {current_tasks_dir}")
        
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
                        
                        print(f"📁 Claiming file operations task: {task_dir.name}")
                        await self.process_task(task_dir)
                        
                    except Exception as e:
                        print(f"Error checking task {task_dir.name}: {e}")
                
            except Exception as e:
                print(f"Error in workspace monitoring: {e}")
            
            await asyncio.sleep(int(os.getenv("TASK_MONITOR_INTERVAL", 3)))

    async def run(self):
        """Run the file operations agent"""
        print("📁 Starting Real File Operations Agent...")
        print("Features:")
        print("- Real file and directory operations")
        print("- Git commit integration")
        print("- Workspace task monitoring")
        print("- Batch operation processing")
        print("- Safe file handling with error checking")
        
        await self.monitor_workspace()
        
# Create agent instance
file_operations_agent = FileOperationsAgent()

if __name__ == "__main__":
    asyncio.run(file_operations_agent.run()) 