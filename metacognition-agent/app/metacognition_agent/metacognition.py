"""
Conscientious Planning Metacognition Engine
Provides internal monologue capabilities and self-reflection for intelligent task orchestration
"""

import os
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

class ReflectionType(Enum):
    """Types of metacognitive reflection"""
    TASK_ANALYSIS = "task_analysis"
    PROGRESS_EVALUATION = "progress_evaluation"
    STRATEGY_REFLECTION = "strategy_reflection"
    AGENT_PERFORMANCE = "agent_performance"
    BOTTLENECK_ANALYSIS = "bottleneck_analysis"
    COMPLETION_ASSESSMENT = "completion_assessment"

class MonologueLevel(Enum):
    """Levels of internal monologue detail"""
    BRIEF = "brief"
    DETAILED = "detailed"
    ANALYTICAL = "analytical"
    REFLECTIVE = "reflective"

@dataclass
class MetacognitiveThought:
    """Represents a single metacognitive thought or reflection"""
    timestamp: datetime
    thought_type: ReflectionType
    content: str
    context: Dict[str, Any]
    confidence: float
    action_items: List[str]
    insights: List[str]

@dataclass
class TaskProgress:
    """Tracks progress of a specific task"""
    task_id: str
    task_description: str
    current_step: int
    total_steps: int
    completion_percentage: float
    status: str
    start_time: datetime
    last_update: datetime
    estimated_completion: Optional[datetime]
    bottlenecks: List[str]
    successes: List[str]
    failures: List[str]

@dataclass
class OrchestrationState:
    """Current state of the orchestration system"""
    active_tasks: List[str]
    available_agents: List[str]
    agent_performance: Dict[str, Dict[str, Any]]
    system_health: Dict[str, Any]
    resource_utilization: Dict[str, float]
    last_reflection: Optional[datetime]

class MetacognitionEngine:
    """Core metacognition engine with internal monologue and self-reflection"""
    
    def __init__(self):
        self.thoughts: List[MetacognitiveThought] = []
        self.task_progress: Dict[str, TaskProgress] = {}
        self.orchestration_state = OrchestrationState(
            active_tasks=[],
            available_agents=[],
            agent_performance={},
            system_health={},
            resource_utilization={},
            last_reflection=None
        )
        self.monologue_level = MonologueLevel.DETAILED
        self.reflection_interval = int(os.getenv("METACOGNITION_REFLECTION_INTERVAL", "60"))
        self.enabled = os.getenv("ENABLE_INTERNAL_MONOLOGUE", "true").lower() == "true"
        
        # Setup logging
        self.logger = logging.getLogger("metacognition")
        self.logger.setLevel(getattr(logging, os.getenv("MONOLOGUE_LOG_LEVEL", "INFO")))
        
        # Do NOT start the reflection loop here; must be started from an async context
        # Call await metacognition_engine.start_reflection_loop() from an async context to start
    
    async def think(self, thought_type: ReflectionType, content: str, context: Dict[str, Any] = None) -> MetacognitiveThought:
        """Generate a metacognitive thought"""
        if not self.enabled:
            return None
        
        thought = MetacognitiveThought(
            timestamp=datetime.now(),
            thought_type=thought_type,
            content=content,
            context=context or {},
            confidence=self._assess_confidence(content, context),
            action_items=self._extract_action_items(content),
            insights=self._extract_insights(content)
        )
        
        self.thoughts.append(thought)
        self.logger.info(f"Metacognitive thought: {thought_type.value} - {content[:100]}...")
        
        return thought
    
    async def reflect_on_task(self, task_id: str, task_description: str) -> MetacognitiveThought:
        """Reflect on a specific task's progress and status"""
        if task_id not in self.task_progress:
            return None
        
        progress = self.task_progress[task_id]
        
        reflection_content = f"""
        Task Reflection for '{task_description}':
        
        Current Status:
        - Progress: {progress.completion_percentage:.1f}% ({progress.current_step}/{progress.total_steps})
        - Status: {progress.status}
        - Time elapsed: {datetime.now() - progress.start_time}
        - Estimated completion: {progress.estimated_completion}
        
        Analysis:
        - Bottlenecks identified: {len(progress.bottlenecks)}
        - Successful steps: {len(progress.successes)}
        - Failed attempts: {len(progress.failures)}
        
        Strategic Assessment:
        - Is the current approach effective?
        - Are there alternative strategies to consider?
        - What resources are needed for completion?
        - How can we optimize the remaining steps?
        """
        
        return await self.think(
            ReflectionType.TASK_ANALYSIS,
            reflection_content,
            {"task_id": task_id, "progress": asdict(progress)}
        )
    
    async def reflect_on_progress(self) -> MetacognitiveThought:
        """Reflect on overall orchestration progress"""
        total_tasks = len(self.task_progress)
        active_tasks = len([t for t in self.task_progress.values() if t.status == "active"])
        completed_tasks = len([t for t in self.task_progress.values() if t.status == "completed"])
        
        avg_completion = sum(t.completion_percentage for t in self.task_progress.values()) / max(total_tasks, 1)
        
        reflection_content = f"""
        Overall Progress Reflection:
        
        System Status:
        - Total tasks: {total_tasks}
        - Active tasks: {active_tasks}
        - Completed tasks: {completed_tasks}
        - Average completion: {avg_completion:.1f}%
        
        Agent Performance:
        - Available agents: {len(self.orchestration_state.available_agents)}
        - Agent utilization: {self.orchestration_state.resource_utilization}
        
        Strategic Insights:
        - Are we making optimal use of available resources?
        - Is the task distribution balanced?
        - Are there systemic bottlenecks?
        - How can we improve overall efficiency?
        """
        
        return await self.think(
            ReflectionType.PROGRESS_EVALUATION,
            reflection_content,
            {"total_tasks": total_tasks, "active_tasks": active_tasks, "avg_completion": avg_completion}
        )
    
    async def reflect_on_strategy(self, current_strategy: str, outcomes: List[Dict[str, Any]]) -> MetacognitiveThought:
        """Reflect on the effectiveness of current strategies"""
        success_rate = len([o for o in outcomes if o.get("success", False)]) / max(len(outcomes), 1)
        avg_duration = sum(o.get("duration", 0) for o in outcomes) / max(len(outcomes), 1)
        
        reflection_content = f"""
        Strategy Reflection:
        
        Current Strategy: {current_strategy}
        
        Performance Metrics:
        - Success rate: {success_rate:.1%}
        - Average duration: {avg_duration:.2f}s
        - Total outcomes: {len(outcomes)}
        
        Strategic Assessment:
        - Is this strategy working effectively?
        - What are the key success factors?
        - What are the main failure points?
        - Should we pivot to a different approach?
        - How can we optimize this strategy?
        """
        
        return await self.think(
            ReflectionType.STRATEGY_REFLECTION,
            reflection_content,
            {"strategy": current_strategy, "success_rate": success_rate, "avg_duration": avg_duration}
        )
    
    async def reflect_on_agent_performance(self, agent_name: str, performance_data: Dict[str, Any]) -> MetacognitiveThought:
        """Reflect on individual agent performance"""
        success_rate = performance_data.get("success_rate", 0)
        avg_response_time = performance_data.get("avg_response_time", 0)
        total_tasks = performance_data.get("total_tasks", 0)
        
        reflection_content = f"""
        Agent Performance Reflection:
        
        Agent: {agent_name}
        
        Performance Metrics:
        - Success rate: {success_rate:.1%}
        - Average response time: {avg_response_time:.2f}s
        - Total tasks handled: {total_tasks}
        
        Assessment:
        - Is this agent performing optimally?
        - Are there patterns in failures?
        - Should we adjust task allocation?
        - Does this agent need additional resources?
        - How does this agent compare to others?
        """
        
        return await self.think(
            ReflectionType.AGENT_PERFORMANCE,
            reflection_content,
            {"agent_name": agent_name, "performance": performance_data}
        )
    
    async def analyze_bottlenecks(self) -> MetacognitiveThought:
        """Analyze system bottlenecks and constraints"""
        bottlenecks = []
        for task in self.task_progress.values():
            bottlenecks.extend(task.bottlenecks)
        
        unique_bottlenecks = list(set(bottlenecks))
        bottleneck_frequency = {b: bottlenecks.count(b) for b in unique_bottlenecks}
        
        reflection_content = f"""
        Bottleneck Analysis:
        
        Identified Bottlenecks:
        {chr(10).join(f"- {b}: {freq} occurrences" for b, freq in bottleneck_frequency.items())}
        
        Analysis:
        - Most common bottleneck: {max(bottleneck_frequency.items(), key=lambda x: x[1])[0] if bottleneck_frequency else "None"}
        - Total bottleneck instances: {len(bottlenecks)}
        - Unique bottleneck types: {len(unique_bottlenecks)}
        
        Recommendations:
        - How can we address the most common bottlenecks?
        - Are there systemic issues causing these bottlenecks?
        - What resources are needed to resolve these issues?
        - Should we restructure the workflow to avoid bottlenecks?
        """
        
        return await self.think(
            ReflectionType.BOTTLENECK_ANALYSIS,
            reflection_content,
            {"bottlenecks": bottleneck_frequency, "total_instances": len(bottlenecks)}
        )
    
    async def assess_completion(self, task_id: str) -> MetacognitiveThought:
        """Assess whether a task is truly complete"""
        if task_id not in self.task_progress:
            return None
        
        progress = self.task_progress[task_id]
        completion_threshold = float(os.getenv("TASK_COMPLETION_THRESHOLD", "0.95"))
        
        is_complete = progress.completion_percentage >= completion_threshold
        quality_score = self._assess_task_quality(progress)
        
        reflection_content = f"""
        Task Completion Assessment:
        
        Task: {progress.task_description}
        Completion Percentage: {progress.completion_percentage:.1f}%
        Quality Score: {quality_score:.2f}
        Threshold: {completion_threshold:.1%}
        
        Assessment:
        - Is the task functionally complete? {is_complete}
        - Are all objectives met?
        - Is the quality acceptable?
        - Are there any loose ends?
        - Should we mark this as complete?
        
        Final Decision:
        - Status: {"COMPLETE" if is_complete else "INCOMPLETE"}
        - Confidence: {self._assess_confidence("Task completion assessment", {"progress": asdict(progress)})}
        """
        
        return await self.think(
            ReflectionType.COMPLETION_ASSESSMENT,
            reflection_content,
            {"task_id": task_id, "is_complete": is_complete, "quality_score": quality_score}
        )
    
    def update_task_progress(self, task_id: str, current_step: int, total_steps: int, status: str, 
                           completion_percentage: float, bottlenecks: List[str] = None, 
                           successes: List[str] = None, failures: List[str] = None):
        """Update progress for a specific task"""
        if task_id not in self.task_progress:
            self.task_progress[task_id] = TaskProgress(
                task_id=task_id,
                task_description="",
                current_step=current_step,
                total_steps=total_steps,
                completion_percentage=completion_percentage,
                status=status,
                start_time=datetime.now(),
                last_update=datetime.now(),
                estimated_completion=None,
                bottlenecks=bottlenecks or [],
                successes=successes or [],
                failures=failures or []
            )
        else:
            progress = self.task_progress[task_id]
            progress.current_step = current_step
            progress.total_steps = total_steps
            progress.completion_percentage = completion_percentage
            progress.status = status
            progress.last_update = datetime.now()
            if bottlenecks:
                progress.bottlenecks.extend(bottlenecks)
            if successes:
                progress.successes.extend(successes)
            if failures:
                progress.failures.extend(failures)
    
    def update_orchestration_state(self, active_tasks: List[str] = None, available_agents: List[str] = None,
                                 agent_performance: Dict[str, Dict[str, Any]] = None,
                                 system_health: Dict[str, Any] = None,
                                 resource_utilization: Dict[str, float] = None):
        """Update the overall orchestration state"""
        if active_tasks is not None:
            self.orchestration_state.active_tasks = active_tasks
        if available_agents is not None:
            self.orchestration_state.available_agents = available_agents
        if agent_performance is not None:
            self.orchestration_state.agent_performance.update(agent_performance)
        if system_health is not None:
            self.orchestration_state.system_health.update(system_health)
        if resource_utilization is not None:
            self.orchestration_state.resource_utilization.update(resource_utilization)
    
    async def _reflection_loop(self):
        """Periodic reflection loop"""
        while True:
            try:
                await asyncio.sleep(self.reflection_interval)
                
                # Perform periodic reflections
                await self.reflect_on_progress()
                await self.analyze_bottlenecks()
                
                self.orchestration_state.last_reflection = datetime.now()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in reflection loop: {e}")
    
    def _assess_confidence(self, content: str, context: Dict[str, Any]) -> float:
        """Assess confidence level in a thought or reflection"""
        # Simple heuristic based on content length and context richness
        confidence = 0.5  # Base confidence
        
        # Adjust based on content length (more detailed = higher confidence)
        if len(content) > 500:
            confidence += 0.2
        elif len(content) > 200:
            confidence += 0.1
        
        # Adjust based on context richness
        if context and len(context) > 3:
            confidence += 0.1
        
        # Adjust based on thought type
        if any(keyword in content.lower() for keyword in ["success", "completed", "achieved"]):
            confidence += 0.1
        elif any(keyword in content.lower() for keyword in ["failed", "error", "bottleneck"]):
            confidence -= 0.1
        
        return min(max(confidence, 0.0), 1.0)
    
    def _extract_action_items(self, content: str) -> List[str]:
        """Extract action items from reflection content"""
        action_items = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('-') and any(keyword in line.lower() for keyword in 
                                          ["should", "need", "must", "will", "can", "could"]):
                action_items.append(line[1:].strip())
        
        return action_items
    
    def _extract_insights(self, content: str) -> List[str]:
        """Extract insights from reflection content"""
        insights = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('-') and any(keyword in line.lower() for keyword in 
                                          ["is", "are", "was", "were", "has", "have", "found", "discovered"]):
                insights.append(line[1:].strip())
        
        return insights
    
    def _assess_task_quality(self, progress: TaskProgress) -> float:
        """Assess the quality of task completion"""
        quality = 0.5  # Base quality
        
        # Adjust based on success/failure ratio
        total_attempts = len(progress.successes) + len(progress.failures)
        if total_attempts > 0:
            success_ratio = len(progress.successes) / total_attempts
            quality += success_ratio * 0.3
        
        # Adjust based on completion percentage
        quality += progress.completion_percentage * 0.2
        
        # Penalize for bottlenecks
        if progress.bottlenecks:
            quality -= min(len(progress.bottlenecks) * 0.05, 0.2)
        
        return min(max(quality, 0.0), 1.0)
    
    def get_recent_thoughts(self, limit: int = 10) -> List[MetacognitiveThought]:
        """Get recent metacognitive thoughts"""
        return sorted(self.thoughts, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_thoughts_by_type(self, thought_type: ReflectionType) -> List[MetacognitiveThought]:
        """Get thoughts of a specific type"""
        return [t for t in self.thoughts if t.thought_type == thought_type]
    
    def export_metacognition_data(self) -> Dict[str, Any]:
        """Export metacognition data for persistence"""
        return {
            "thoughts": [asdict(t) for t in self.thoughts],
            "task_progress": {k: asdict(v) for k, v in self.task_progress.items()},
            "orchestration_state": asdict(self.orchestration_state),
            "export_timestamp": datetime.now().isoformat()
        }

    async def start_reflection_loop(self):
        """Start the background reflection loop. Call this from an async context."""
        if self.enabled:
            asyncio.create_task(self._reflection_loop())

# Global metacognition engine instance
metacognition_engine = MetacognitionEngine() 