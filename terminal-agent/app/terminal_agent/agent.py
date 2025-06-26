"""
Terminal Agent
Specialized ADK agent for all shell and terminal operations
"""

import os
import asyncio
import json
import subprocess
import shlex
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

class TerminalAgent(Agent):
    """Specialized agent for all shell and terminal operations"""
    
    def __init__(self, name: str = "terminal_agent", model: str = None):
        # Single-purpose tools - only terminal operations
        tools = [
            FunctionTool(self.run_command),
            FunctionTool(self.run_script),
            FunctionTool(self.execute_command_sequence)
        ]
        
        super().__init__(
            name=name,
            model=model or os.getenv("TERMINAL_MODEL", "gemini-2.0-flash-live-001"),
            description="Terminal operations specialist for all shell and command-line tasks",
            instruction="""You are a terminal operations specialist. Your ONLY job is to execute shell commands, scripts, and terminal operations safely and efficiently.

Your capabilities include:
1. **Single Commands**: Execute any shell command (find, grep, ls, cat, curl, git, npm, pip, etc.)
2. **Command Sequences**: Execute multiple related commands in sequence
3. **Script Execution**: Run shell scripts and batch operations
4. **Safe Execution**: Validate commands for safety before execution
5. **Output Processing**: Capture and format command outputs properly

When you see a terminal task:
1. Analyze what commands need to be executed
2. Validate commands for safety (no destructive operations without confirmation)
3. Execute commands with proper error handling
4. Capture and format outputs clearly
5. Save results to workspace for other agents

Examples of commands you handle:
- File operations: find, ls, cat, head, tail, grep, awk, sed
- Development: git, npm, pip, docker, kubectl
- System: ps, top, df, du, netstat, curl, wget
- Analysis: wc, sort, uniq, diff, md5sum

Keep it safe, reliable, and well-documented.""",
            tools=tools
        )
        
        # Store workspace path in global scope since ADK Agent doesn't allow custom attributes
        global workspace_path, current_tasks_dir, safe_commands, require_confirmation
        workspace_path = Path(os.getenv("TASK_WORKSPACE_PATH", "./workspace"))
        current_tasks_dir = workspace_path / "current_tasks"
        
        # Safety settings (global since ADK doesn't allow custom attributes)
        safe_commands = {
            # Read operations
            'find', 'ls', 'cat', 'head', 'tail', 'grep', 'awk', 'sed', 'sort', 'uniq', 'wc', 'diff',
            # Development tools (read operations)
            'git log', 'git status', 'git diff', 'git show', 'git branch',
            'npm list', 'pip list', 'pip show',
            # System info (read operations)
            'ps', 'top', 'df', 'du', 'netstat', 'curl', 'wget', 'which', 'whereis',
            # Analysis tools
            'md5sum', 'sha256sum', 'file', 'stat', 'date', 'whoami', 'id'
        }
        
        require_confirmation = {
            # Potentially destructive operations
            'rm', 'rmdir', 'mv', 'cp', 'chmod', 'chown', 'sudo',
            'git add', 'git commit', 'git push', 'git pull', 'git merge',
            'npm install', 'pip install', 'apt install', 'yum install',
            'docker run', 'docker build', 'kubectl apply'
        }
    
    async def run_command(self, command: str, working_dir: Optional[str] = None, timeout: int = 30) -> Dict[str, Any]:
        """Execute a single shell command
        
        Args:
            command: The shell command to execute
            working_dir: Optional working directory (defaults to current workspace)
            timeout: Command timeout in seconds
            
        Returns:
            Dict containing command results
        """
        try:
            print(f"💻 Executing command: {command}")
            
            # Safety check
            safety_check = self._check_command_safety(command)
            if not safety_check["safe"]:
                return {
                    "success": False,
                    "error": f"Command blocked for safety: {safety_check['reason']}",
                    "command": command,
                    "suggestion": safety_check.get("suggestion", "")
                }
            
            # Set working directory
            work_dir = working_dir or str(workspace_path)
            
            # Execute command safely
            result = await self._execute_command_safely(command, work_dir, timeout)
            
            print(f"✅ Command completed: {result.get('return_code', 'unknown')} exit code")
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Command execution failed: {str(e)}",
                "command": command
            }
            print(f"❌ Command failed: {e}")
            return error_result
    
    async def run_script(self, script_content: str, script_type: str = "bash", working_dir: Optional[str] = None) -> Dict[str, Any]:
        """Execute a shell script
        
        Args:
            script_content: The script content to execute
            script_type: Type of script (bash, sh, python, etc.)
            working_dir: Optional working directory
            
        Returns:
            Dict containing script execution results
        """
        try:
            print(f"📜 Executing {script_type} script ({len(script_content)} chars)")
            
            # Safety check for script content
            safety_check = self._check_script_safety(script_content)
            if not safety_check["safe"]:
                return {
                    "success": False,
                    "error": f"Script blocked for safety: {safety_check['reason']}",
                    "script_type": script_type,
                    "suggestion": safety_check.get("suggestion", "")
                }
            
            # Create temporary script file
            work_dir = working_dir or str(workspace_path)
            script_path = await self._create_temp_script(script_content, script_type, work_dir)
            
            # Execute script
            if script_type == "python":
                command = f"python {script_path}"
            elif script_type in ["bash", "sh"]:
                command = f"bash {script_path}"
            else:
                command = f"{script_type} {script_path}"
            
            result = await self._execute_command_safely(command, work_dir, timeout=60)
            
            # Clean up temporary script
            try:
                os.unlink(script_path)
            except:
                pass
            
            print(f"✅ Script completed: {result.get('return_code', 'unknown')} exit code")
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Script execution failed: {str(e)}",
                "script_type": script_type
            }
            print(f"❌ Script failed: {e}")
            return error_result
    
    async def execute_command_sequence(self, commands: List[str], working_dir: Optional[str] = None, stop_on_error: bool = True) -> Dict[str, Any]:
        """Execute a sequence of commands
        
        Args:
            commands: List of commands to execute in sequence
            working_dir: Optional working directory
            stop_on_error: Whether to stop sequence if a command fails
            
        Returns:
            Dict containing sequence execution results
        """
        try:
            print(f"🔄 Executing command sequence: {len(commands)} commands")
            
            work_dir = working_dir or str(workspace_path)
            results = []
            
            for i, command in enumerate(commands, 1):
                print(f"  📋 Step {i}/{len(commands)}: {command}")
                
                # Execute command
                result = await self.run_command(command, work_dir)
                results.append({
                    "step": i,
                    "command": command,
                    "result": result
                })
                
                # Check if we should stop on error
                if not result.get("success", False) and stop_on_error:
                    print(f"❌ Sequence stopped at step {i} due to error")
                    break
            
            # Calculate overall success
            successful_steps = len([r for r in results if r["result"].get("success", False)])
            overall_success = successful_steps == len(commands)
            
            sequence_result = {
                "success": overall_success,
                "total_commands": len(commands),
                "successful_commands": successful_steps,
                "results": results,
                "stopped_early": not overall_success and stop_on_error
            }
            
            print(f"✅ Sequence complete: {successful_steps}/{len(commands)} successful")
            return sequence_result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Command sequence failed: {str(e)}",
                "total_commands": len(commands)
            }
            print(f"❌ Sequence failed: {e}")
            return error_result
    
    def _check_command_safety(self, command: str) -> Dict[str, Any]:
        """Check if a command is safe to execute"""
        command_lower = command.lower().strip()
        
        # Check for dangerous patterns
        dangerous_patterns = [
            'rm -rf /', 'sudo rm', 'format', 'fdisk', 'mkfs',
            'dd if=', '> /dev/', 'chmod 777', 'chown root',
            'curl | sh', 'wget | sh', 'eval', 'exec'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                return {
                    "safe": False,
                    "reason": f"Contains dangerous pattern: {pattern}",
                    "suggestion": "Use safer alternatives or get explicit confirmation"
                }
        
        # Check if command needs confirmation
        command_parts = shlex.split(command_lower)
        if command_parts:
            base_command = command_parts[0]
            for confirm_cmd in require_confirmation:
                if base_command.startswith(confirm_cmd) or confirm_cmd in command_lower:
                    return {
                        "safe": False,
                        "reason": f"Command requires confirmation: {confirm_cmd}",
                        "suggestion": "Add explicit confirmation or use --dry-run first"
                    }
        
        return {"safe": True}
    
    def _check_script_safety(self, script_content: str) -> Dict[str, Any]:
        """Check if script content is safe to execute"""
        content_lower = script_content.lower()
        
        # Check for dangerous script patterns
        dangerous_script_patterns = [
            'rm -rf', 'sudo', 'curl | sh', 'wget | sh',
            'eval', 'exec', 'system(', 'os.system',
            'subprocess.call', 'format', 'fdisk'
        ]
        
        for pattern in dangerous_script_patterns:
            if pattern in content_lower:
                return {
                    "safe": False,
                    "reason": f"Script contains dangerous pattern: {pattern}",
                    "suggestion": "Review script content for safety"
                }
        
        return {"safe": True}
    
    async def _execute_command_safely(self, command: str, working_dir: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute a command safely with proper error handling"""
        try:
            # Use asyncio subprocess for better control
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=1024*1024  # 1MB limit for output
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    "success": False,
                    "error": f"Command timed out after {timeout} seconds",
                    "command": command,
                    "return_code": -1
                }
            
            # Decode output
            stdout_text = stdout.decode('utf-8', errors='replace')
            stderr_text = stderr.decode('utf-8', errors='replace')
            
            # Determine success based on return code
            success = process.returncode == 0
            
            return {
                "success": success,
                "command": command,
                "return_code": process.returncode,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "working_dir": working_dir,
                "execution_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}",
                "command": command
            }
    
    async def _create_temp_script(self, content: str, script_type: str, working_dir: str) -> str:
        """Create a temporary script file"""
        import tempfile
        
        # Determine file extension
        extensions = {
            "bash": ".sh",
            "sh": ".sh", 
            "python": ".py",
            "javascript": ".js",
            "node": ".js"
        }
        
        ext = extensions.get(script_type, ".sh")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=ext,
            dir=working_dir,
            delete=False
        ) as f:
            f.write(content)
            temp_path = f.name
        
        # Make script executable
        os.chmod(temp_path, 0o755)
        
        return temp_path
    
    async def monitor_workspace(self):
        """Monitor workspace for terminal tasks"""
        print(f"💻 {self.name} monitoring workspace for terminal tasks...")
        
        while True:
            try:
                terminal_tasks = self._find_terminal_tasks()
                
                for task in terminal_tasks:
                    print(f"🖥️  Found terminal task: {task['task_id']}")
                    self._claim_task(task)
                    
                    # Execute the terminal task
                    result = await self._execute_terminal_task(task)
                    
                    if result.get("success"):
                        self._mark_task_completed(task, result)
                        print(f"✅ Completed terminal task {task['task_id']}")
                    else:
                        self._mark_task_failed(task, result)
                        print(f"❌ Failed terminal task {task['task_id']}")
                
                await asyncio.sleep(3)  # Check every 3 seconds
                
            except Exception as e:
                print(f"❌ Error in workspace monitoring: {e}")
                await asyncio.sleep(5)
    
    def _find_terminal_tasks(self) -> List[Dict[str, Any]]:
        """Find tasks that need terminal operations"""
        terminal_tasks = []
        
        try:
            if not current_tasks_dir.exists():
                return terminal_tasks
                
            for task_dir in current_tasks_dir.iterdir():
                if not task_dir.is_dir():
                    continue
                    
                task_file = task_dir / "task.json"
                if not task_file.exists():
                    continue
                
                with open(task_file, 'r') as f:
                    task = json.load(f)
                
                # Look for tasks that need terminal operations
                if (self._is_terminal_task(task) and
                    task.get("status") in ["available", "not_started"] and
                    not self._is_task_claimed(task)):
                    
                    terminal_tasks.append(task)
                    
        except Exception as e:
            print(f"❌ Error finding terminal tasks: {e}")
        
        return terminal_tasks
    
    def _is_terminal_task(self, task: Dict[str, Any]) -> bool:
        """Determine if a task needs terminal operations"""
        # Check agent_type
        if task.get("agent_type") == "terminal":
            return True
        
        # Check description for terminal indicators
        description = task.get("description", "").lower()
        terminal_indicators = [
            "run command", "execute", "find ", "grep ", "ls ", "cat ",
            "git ", "npm ", "pip ", "curl ", "wget ", "bash ", "shell",
            "command", "terminal", "script", "awk ", "sed ", "sort "
        ]
        
        return any(indicator in description for indicator in terminal_indicators)
    
    async def _execute_terminal_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a terminal task based on its requirements"""
        try:
            task_description = task.get("description", "")
            specific_commands = task.get("specific_commands", [])
            
            if specific_commands:
                # Execute specific commands provided by planning
                print(f"📋 Executing {len(specific_commands)} planned commands")
                result = await self.execute_command_sequence(specific_commands)
                
                # Save results to workspace
                self._save_task_results(task, result)
                
                return result
            else:
                # Extract command from description (simplified approach)
                command = self._extract_command_from_description(task_description)
                if command:
                    result = await self.run_command(command)
                    self._save_task_results(task, result)
                    return result
                else:
                    return {
                        "success": False,
                        "error": "Could not determine command to execute",
                        "task_description": task_description
                    }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Terminal task execution failed: {str(e)}",
                "task_id": task.get("task_id")
            }
    
    def _extract_command_from_description(self, description: str) -> Optional[str]:
        """Extract a command from task description (simplified)"""
        # This is a simple extraction - in a real system, this would be more sophisticated
        if "find" in description and "name" in description:
            if "*.py" in description:
                return "find . -name '*.py' | head -20"
            elif "*.js" in description:
                return "find . -name '*.js' | head -20"
            else:
                return "find . -type f | head -20"
        elif "git status" in description:
            return "git status"
        elif "list" in description and "file" in description:
            return "ls -la"
        else:
            return None
    
    def _save_task_results(self, task: Dict[str, Any], result: Dict[str, Any]):
        """Save task execution results to workspace"""
        try:
            task_dir = current_tasks_dir / task["task_id"]
            results_file = task_dir / "terminal_results.json"
            
            with open(results_file, 'w') as f:
                json.dump({
                    "execution_time": datetime.now().isoformat(),
                    "agent": self.name,
                    "task_description": task.get("description"),
                    "result": result
                }, f, indent=2)
                
            print(f"💾 Saved results to {results_file}")
            
        except Exception as e:
            print(f"❌ Failed to save task results: {e}")
    
    def _is_task_claimed(self, task: Dict[str, Any]) -> bool:
        """Check if task is already claimed by an agent"""
        return task.get("status") in ["claimed", "in_progress", "completed"]
    
    def _claim_task(self, task: Dict[str, Any]):
        """Claim a task by updating its status"""
        try:
            task["status"] = "claimed"
            task["claimed_by"] = self.name
            task["claimed_at"] = datetime.now().isoformat()
            
            task_dir = current_tasks_dir / task["task_id"]
            task_file = task_dir / "task.json"
            
            with open(task_file, 'w') as f:
                json.dump(task, f, indent=2)
                
        except Exception as e:
            print(f"❌ Failed to claim task {task['task_id']}: {e}")
    
    def _mark_task_completed(self, task: Dict[str, Any], result: Dict[str, Any]):
        """Mark a task as completed"""
        try:
            task["status"] = "completed"
            task["completed_by"] = self.name
            task["completed_at"] = datetime.now().isoformat()
            task["terminal_result"] = {
                "success": result.get("success"),
                "return_code": result.get("return_code"),
                "output_length": len(result.get("stdout", ""))
            }
            
            task_dir = current_tasks_dir / task["task_id"]
            task_file = task_dir / "task.json"
            
            with open(task_file, 'w') as f:
                json.dump(task, f, indent=2)
                
        except Exception as e:
            print(f"❌ Failed to mark task completed {task['task_id']}: {e}")
    
    def _mark_task_failed(self, task: Dict[str, Any], result: Dict[str, Any]):
        """Mark a task as failed"""
        try:
            task["status"] = "failed"
            task["failed_by"] = self.name
            task["failed_at"] = datetime.now().isoformat()
            task["failure_reason"] = result.get("error", "Unknown error")
            task["retry_count"] = task.get("retry_count", 0) + 1
            
            task_dir = current_tasks_dir / task["task_id"]
            task_file = task_dir / "task.json"
            
            with open(task_file, 'w') as f:
                json.dump(task, f, indent=2)
                
        except Exception as e:
            print(f"❌ Failed to mark task failed {task['task_id']}: {e}")

# Create the agent instance
terminal_agent = TerminalAgent()

if __name__ == "__main__":
    async def main():
        """Main entry point for the terminal agent"""
        print("💻 Starting Terminal Agent...")
        print("Specialization: All shell and terminal operations")
        print("Framework: Google ADK")
        print("Safety: Command validation enabled")
        print("Workspace monitoring: ENABLED")
        
        # Start monitoring workspace
        await terminal_agent.monitor_workspace()
    
    asyncio.run(main()) 