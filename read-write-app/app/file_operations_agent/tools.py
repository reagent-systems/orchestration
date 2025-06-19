"""
File Operations Tools for ADK Agents
Provides tools for reading, writing, and managing files in a git workspace
"""

import os
import git
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from google.adk.tools import FunctionTool
from google.adk.annotations import Schema

class FileOperationsTools:
    """Collection of file operation tools for agents"""
    
    def __init__(self, workspace_path: str = "./workspace"):
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(exist_ok=True)
        self.repo = None
        self._initialize_git_repo()
    
    def _initialize_git_repo(self):
        """Initialize or connect to git repository"""
        try:
            if (self.workspace_path / ".git").exists():
                self.repo = git.Repo(self.workspace_path)
                print(f"Connected to existing git repo: {self.repo.working_dir}")
            else:
                # Initialize new repo if GIT_REPO_URL is provided
                repo_url = os.getenv("GIT_REPO_URL")
                if repo_url:
                    self.repo = git.Repo.clone_from(repo_url, self.workspace_path)
                    print(f"Cloned git repo from: {repo_url}")
                else:
                    self.repo = git.Repo.init(self.workspace_path)
                    print(f"Initialized new git repo at: {self.workspace_path}")
                
                # Configure git user
                self.repo.config_writer().set_value("user", "name", 
                    os.getenv("GIT_USER_NAME", "Agent User")).release()
                self.repo.config_writer().set_value("user", "email", 
                    os.getenv("GIT_USER_EMAIL", "agent@example.com")).release()
        except Exception as e:
            print(f"Git initialization failed: {e}")
            self.repo = None
    
    @FunctionTool(
        name="read_file",
        description="Read the contents of a file in the workspace"
    )
    def read_file(
        self,
        file_path: str = Schema(description="Path to the file relative to workspace root")
    ) -> Dict[str, Any]:
        """Read a file from the workspace"""
        try:
            full_path = self.workspace_path / file_path
            if not full_path.exists():
                return {"error": f"File not found: {file_path}"}
            
            if not full_path.is_file():
                return {"error": f"Path is not a file: {file_path}"}
            
            # Check file size limit
            file_size_mb = full_path.stat().st_size / (1024 * 1024)
            max_size = float(os.getenv("MAX_FILE_SIZE_MB", "10"))
            if file_size_mb > max_size:
                return {"error": f"File too large: {file_size_mb:.2f}MB (max: {max_size}MB)"}
            
            # Read file content
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "file_path": file_path,
                "content": content,
                "size_bytes": len(content),
                "size_mb": file_size_mb
            }
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}
    
    @FunctionTool(
        name="write_file",
        description="Write content to a file in the workspace"
    )
    def write_file(
        self,
        file_path: str = Schema(description="Path to the file relative to workspace root"),
        content: str = Schema(description="Content to write to the file"),
        overwrite: bool = Schema(description="Whether to overwrite existing file", default=True)
    ) -> Dict[str, Any]:
        """Write content to a file in the workspace"""
        try:
            full_path = self.workspace_path / file_path
            
            # Check if file exists and overwrite setting
            if full_path.exists() and not overwrite:
                return {"error": f"File already exists and overwrite=False: {file_path}"}
            
            # Create parent directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file content
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Git operations if enabled
            if self.repo and os.getenv("ENABLE_GIT_OPERATIONS", "true").lower() == "true":
                self._git_add_and_commit(file_path, "Write file")
            
            return {
                "success": True,
                "file_path": file_path,
                "bytes_written": len(content),
                "git_committed": bool(self.repo and os.getenv("ENABLE_GIT_OPERATIONS", "true").lower() == "true")
            }
        except Exception as e:
            return {"error": f"Failed to write file: {str(e)}"}
    
    @FunctionTool(
        name="list_files",
        description="List files and directories in the workspace"
    )
    def list_files(
        self,
        directory: str = Schema(description="Directory to list (relative to workspace root)", default="."),
        recursive: bool = Schema(description="Whether to list recursively", default=False)
    ) -> Dict[str, Any]:
        """List files and directories in the workspace"""
        try:
            target_path = self.workspace_path / directory
            if not target_path.exists():
                return {"error": f"Directory not found: {directory}"}
            
            if not target_path.is_dir():
                return {"error": f"Path is not a directory: {directory}"}
            
            files = []
            dirs = []
            
            if recursive:
                for item in target_path.rglob("*"):
                    if item.is_file():
                        files.append(str(item.relative_to(self.workspace_path)))
                    elif item.is_dir():
                        dirs.append(str(item.relative_to(self.workspace_path)))
            else:
                for item in target_path.iterdir():
                    if item.is_file():
                        files.append(str(item.relative_to(self.workspace_path)))
                    elif item.is_dir():
                        dirs.append(str(item.relative_to(self.workspace_path)))
            
            return {
                "success": True,
                "directory": directory,
                "files": sorted(files),
                "directories": sorted(dirs),
                "total_files": len(files),
                "total_directories": len(dirs)
            }
        except Exception as e:
            return {"error": f"Failed to list files: {str(e)}"}
    
    @FunctionTool(
        name="delete_file",
        description="Delete a file from the workspace"
    )
    def delete_file(
        self,
        file_path: str = Schema(description="Path to the file to delete relative to workspace root")
    ) -> Dict[str, Any]:
        """Delete a file from the workspace"""
        try:
            full_path = self.workspace_path / file_path
            
            if not full_path.exists():
                return {"error": f"File not found: {file_path}"}
            
            if not full_path.is_file():
                return {"error": f"Path is not a file: {file_path}"}
            
            # Delete the file
            full_path.unlink()
            
            # Git operations if enabled
            if self.repo and os.getenv("ENABLE_GIT_OPERATIONS", "true").lower() == "true":
                self._git_add_and_commit(file_path, "Delete file")
            
            return {
                "success": True,
                "file_path": file_path,
                "deleted": True,
                "git_committed": bool(self.repo and os.getenv("ENABLE_GIT_OPERATIONS", "true").lower() == "true")
            }
        except Exception as e:
            return {"error": f"Failed to delete file: {str(e)}"}
    
    @FunctionTool(
        name="create_directory",
        description="Create a directory in the workspace"
    )
    def create_directory(
        self,
        directory_path: str = Schema(description="Path to the directory to create relative to workspace root")
    ) -> Dict[str, Any]:
        """Create a directory in the workspace"""
        try:
            full_path = self.workspace_path / directory_path
            
            if full_path.exists():
                return {"error": f"Directory already exists: {directory_path}"}
            
            # Create directory
            full_path.mkdir(parents=True, exist_ok=True)
            
            # Git operations if enabled
            if self.repo and os.getenv("ENABLE_GIT_OPERATIONS", "true").lower() == "true":
                self._git_add_and_commit(directory_path, "Create directory")
            
            return {
                "success": True,
                "directory_path": directory_path,
                "created": True,
                "git_committed": bool(self.repo and os.getenv("ENABLE_GIT_OPERATIONS", "true").lower() == "true")
            }
        except Exception as e:
            return {"error": f"Failed to create directory: {str(e)}"}
    
    @FunctionTool(
        name="git_status",
        description="Get the current git status of the workspace"
    )
    def git_status(self) -> Dict[str, Any]:
        """Get git status information"""
        try:
            if not self.repo:
                return {"error": "Git repository not initialized"}
            
            # Get status
            status = self.repo.git.status()
            
            # Get current branch
            current_branch = self.repo.active_branch.name
            
            # Get last commit
            last_commit = self.repo.head.commit.hexsha[:8] if self.repo.head.commit else None
            
            return {
                "success": True,
                "status": status,
                "current_branch": current_branch,
                "last_commit": last_commit,
                "is_dirty": self.repo.is_dirty()
            }
        except Exception as e:
            return {"error": f"Failed to get git status: {str(e)}"}
    
    @FunctionTool(
        name="git_commit",
        description="Commit changes to git repository"
    )
    def git_commit(
        self,
        message: str = Schema(description="Commit message"),
        files: Optional[List[str]] = Schema(description="Specific files to commit", default=None)
    ) -> Dict[str, Any]:
        """Commit changes to git repository"""
        try:
            if not self.repo:
                return {"error": "Git repository not initialized"}
            
            # Add files
            if files:
                for file_path in files:
                    full_path = self.workspace_path / file_path
                    if full_path.exists():
                        self.repo.index.add([str(full_path)])
            else:
                self.repo.index.add("*")
            
            # Check if there are changes to commit
            if not self.repo.index.diff("HEAD"):
                return {"error": "No changes to commit"}
            
            # Create commit message with prefix
            prefix = os.getenv("COMMIT_MESSAGE_PREFIX", "[Agent]")
            full_message = f"{prefix} {message}"
            
            # Commit
            commit = self.repo.index.commit(full_message)
            
            return {
                "success": True,
                "commit_hash": commit.hexsha,
                "commit_message": full_message,
                "files_committed": len(self.repo.index.diff("HEAD"))
            }
        except Exception as e:
            return {"error": f"Failed to commit: {str(e)}"}
    
    def _git_add_and_commit(self, file_path: str, action: str):
        """Helper method to add and commit a file"""
        try:
            if not self.repo:
                return
            
            full_path = self.workspace_path / file_path
            if full_path.exists():
                self.repo.index.add([str(full_path)])
                
                if os.getenv("AUTO_COMMIT", "true").lower() == "true":
                    prefix = os.getenv("COMMIT_MESSAGE_PREFIX", "[Agent]")
                    message = f"{prefix} {action}: {file_path}"
                    self.repo.index.commit(message)
        except Exception as e:
            print(f"Git operation failed: {e}")

# Create global instance
file_tools = FileOperationsTools(os.getenv("GIT_WORKSPACE_PATH", "./workspace")) 