from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Union, Any, Dict, Sequence
from uuid import uuid4

from isek.agent.base import BaseAgent, AgentCard
from isek.memory.memory import Memory
from isek.models.base import Model
from isek.tools.toolkit import Toolkit
from isek.utils.log import log
from isek.utils.print_utils import print_response


@dataclass
class IsekAgent(BaseAgent):
    """Ultra-simplified Agent class with minimal features."""

    # Agent name
    name: Optional[str] = None
    # Agent UUID (autogenerated if not set)
    agent_id: Optional[str] = None
    # Model for this Agent
    model: Optional[Model] = None
    # Agent memory
    memory: Optional[Memory] = None
    # Tools provided to the Model
    tools: Optional[List[Toolkit]] = None
    # A description of the Agent
    description: Optional[str] = None
    # Success criteria for the task
    success_criteria: Optional[str] = None
    # List of instructions for the agent
    instructions: Optional[Union[str, List[str], Callable]] = None
    # Enable debug logs
    debug_mode: bool = False

    def __post_init__(self):
        """Initialize the agent after creation."""
        # Call parent __init__ if not already called
        if not hasattr(self, "agent_id"):
            super().__init__(
                name=self.name,
                agent_id=self.agent_id,
                model=self.model,
                memory=self.memory,
                tools=self.tools,
                description=self.description,
                success_criteria=self.success_criteria,
                instructions=self.instructions,
                debug_mode=self.debug_mode,
            )

    def run(
        self,
        message: str,
        user_id: str = "default",
        session_id: Optional[str] = None,
        messages: Optional[List[Union[Dict, Any]]] = None,
        audio: Optional[Sequence[Any]] = None,
        images: Optional[Sequence[Any]] = None,
        videos: Optional[Sequence[Any]] = None,
        files: Optional[Sequence[Any]] = None,
        stream: Optional[bool] = None,
        stream_intermediate_steps: bool = False,
        knowledge_filters: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> str:
        """Run the agent with a message and return the response."""
        if self.model is None:
            raise ValueError("Model is required to run the agent")

        # Generate session ID if not provided
        if session_id is None:
            session_id = str(uuid4())

        # Prepare messages using the base class method
        messages = self._prepare_messages(message, user_id)

        # Prepare tools parameter using the base class method
        tools_param = self._prepare_tools_parameter()

        # Call the model - it will handle tool calling internally
        response = self.model.response(
            messages=messages,
            tools=tools_param,
            toolkits=self.tools or [],  # Pass actual toolkits for execution
        )

        response_content = response.content or "No response generated"

        # Store in memory if available
        if self.memory:
            self._store_conversation(user_id, session_id, message, response_content)

        if self.debug_mode:
            log.debug(f"Session ID: {session_id}")
            log.debug(f"User ID: {user_id}")
            log.debug(f"User message: {message}")
            log.debug(f"Model response: {response_content}")
            if tools_param:
                log.debug(f"Tools: {tools_param}")

        return response_content

    def print_response(self, *args, **kwargs):
        """
        Proxy to the shared print_response utility, passing self.run as run_func.
        """
        return print_response(self.run, *args, **kwargs)

    def get_agent_card(self) -> AgentCard:
        """Get metadata about the agent for discovery and identification purposes."""
        capabilities = []
        if self.has_memory():
            capabilities.append("memory")
        if self.has_tools():
            capabilities.append("tools")
        if self.has_model():
            capabilities.append("llm")

        model_type = type(self.model).__name__ if self.model else "None"

        return AgentCard(
            name=self.name or "Unnamed Agent",
            description=self.description or "No description",
            capabilities=capabilities,
            tools=self.get_available_tools(),
            model_type=model_type,
        )

    def __repr__(self) -> str:
        return f"IsekAgent(name='{self.name}', id='{self.agent_id}')"
