"""
A2A Configuration and Management for File Operations
Handles A2A protocol settings, agent discovery, and integration configuration
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class A2AAgentInfo:
    """Information about an A2A agent"""
    name: str
    endpoint: str
    capabilities: List[str]
    description: str
    auth_token: Optional[str] = None

class A2AConfig:
    """A2A configuration manager for file operations"""
    
    def __init__(self):
        self.host = os.getenv("A2A_HOST", "localhost")
        self.port = int(os.getenv("A2A_PORT", "8080"))
        self.auth_token = os.getenv("A2A_AUTH_TOKEN")
        self.discovery_interval = int(os.getenv("A2A_DISCOVERY_INTERVAL", "300"))
        self.max_external_agents = int(os.getenv("MAX_EXTERNAL_AGENTS", "10"))
        self.enabled = os.getenv("ENABLE_A2A_INTEGRATION", "true").lower() == "true"
        
        # Registry of discovered agents
        self.agent_registry: Dict[str, A2AAgentInfo] = {}
        
        # Discovery task
        self._discovery_task: Optional[asyncio.Task] = None
    
    def get_endpoint_url(self) -> str:
        """Get the A2A endpoint URL"""
        return f"http://{self.host}:{self.port}"
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for A2A requests"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    async def start_discovery(self):
        """Start periodic agent discovery"""
        if not self.enabled:
            print("A2A integration is disabled")
            return
        
        if self._discovery_task and not self._discovery_task.done():
            print("Discovery task already running")
            return
        
        self._discovery_task = asyncio.create_task(self._discovery_loop())
        print(f"A2A discovery started with {self.discovery_interval}s interval")
    
    async def stop_discovery(self):
        """Stop periodic agent discovery"""
        if self._discovery_task and not self._discovery_task.done():
            self._discovery_task.cancel()
            try:
                await self._discovery_task
            except asyncio.CancelledError:
                pass
            print("A2A discovery stopped")
    
    async def _discovery_loop(self):
        """Main discovery loop"""
        while True:
            try:
                await self._discover_agents()
                await asyncio.sleep(self.discovery_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in A2A discovery loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _discover_agents(self):
        """Discover available A2A agents for file operations"""
        try:
            # This would use the A2A SDK to discover agents
            # For now, we'll simulate discovery with file operation specific agents
            example_agents = [
                A2AAgentInfo(
                    name="code_analyzer_agent",
                    endpoint=f"{self.get_endpoint_url()}/code_analyzer",
                    capabilities=["code_analysis", "syntax_checking", "code_review"],
                    description="Analyzes code files for quality, syntax, and best practices"
                ),
                A2AAgentInfo(
                    name="document_processor_agent",
                    endpoint=f"{self.get_endpoint_url()}/document_processor",
                    capabilities=["document_processing", "text_extraction", "format_conversion"],
                    description="Processes documents and extracts information from various formats"
                ),
                A2AAgentInfo(
                    name="image_processor_agent",
                    endpoint=f"{self.get_endpoint_url()}/image_processor",
                    capabilities=["image_processing", "image_analysis", "image_conversion"],
                    description="Processes and analyzes image files"
                ),
                A2AAgentInfo(
                    name="data_analyzer_agent",
                    endpoint=f"{self.get_endpoint_url()}/data_analyzer",
                    capabilities=["data_analysis", "statistics", "data_visualization"],
                    description="Analyzes data files and provides statistical insights"
                ),
                A2AAgentInfo(
                    name="backup_manager_agent",
                    endpoint=f"{self.get_endpoint_url()}/backup_manager",
                    capabilities=["backup_management", "file_synchronization", "version_control"],
                    description="Manages file backups and synchronization"
                )
            ]
            
            # Update registry
            for agent in example_agents:
                self.agent_registry[agent.name] = agent
            
            print(f"Discovered {len(example_agents)} A2A agents for file operations")
            
        except Exception as e:
            print(f"Error discovering A2A agents: {e}")
    
    def get_agent_by_capability(self, capability: str) -> Optional[A2AAgentInfo]:
        """Find an agent that has the specified capability"""
        for agent in self.agent_registry.values():
            if capability in agent.capabilities:
                return agent
        return None
    
    def get_all_agents(self) -> List[A2AAgentInfo]:
        """Get all discovered agents"""
        return list(self.agent_registry.values())
    
    def get_agent_count(self) -> int:
        """Get the number of discovered agents"""
        return len(self.agent_registry)
    
    def get_agents_for_file_operation(self, operation: str) -> List[A2AAgentInfo]:
        """Get agents suitable for a specific file operation"""
        operation_capabilities = {
            "read": ["document_processing", "text_extraction"],
            "write": ["document_processing", "format_conversion"],
            "analyze": ["code_analysis", "data_analysis", "image_analysis"],
            "backup": ["backup_management", "file_synchronization"],
            "convert": ["format_conversion", "image_conversion"]
        }
        
        capabilities = operation_capabilities.get(operation, [])
        suitable_agents = []
        
        for agent in self.agent_registry.values():
            if any(cap in agent.capabilities for cap in capabilities):
                suitable_agents.append(agent)
        
        return suitable_agents

# Global A2A configuration instance
a2a_config = A2AConfig() 