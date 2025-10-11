from typing import Any, AsyncGenerator, Dict
from pydantic_ai import Agent
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState, AgentCard
from a2a.utils import new_agent_text_message, new_task
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from isek.utils.common import (
    log_agent_activity,
    log_agent_request,
    log_agent_response,
    log_error,
)
from a2a.server.agent_execution.agent_executor import AgentExecutor


# --- Revised Imports ---

ResponsePayload = Dict[str, Any]


class PydanticAIAgentWrapper:
    """Wrap a :class:`pydantic_ai.Agent` instance with a uniform streaming interface.

    The wrapper standardises the input/output contract for use inside the ISEK
    ecosystem and adds rich logging for observability.
    """

    def __init__(self, agent: Agent, agent_card: AgentCard) -> None:
        """Create a new wrapper around *agent*.

        Parameters
        ----------
        agent:
            The underlying **pydantic-ai** agent to delegate the actual reasoning
            work to.
        """
        self._agent: Agent = agent
        self._agent_card: AgentCard = agent_card

        log_agent_activity(self._agent_card.name, "Initialized with GPT-4 model")

    async def invoke(self, query: str, context_id: str) -> ResponsePayload:
        """Run the agent and return the *final* response.

        This convenience wrapper is useful when the caller is not interested in
        the intermediate streaming messages produced by :meth:`stream`.
        """
        log_agent_request(self._agent_card.name, query, context_id)

        try:
            log_agent_activity(
                self._agent_card.name, f"Invoking agent with query: {query}"
            )
            response = await self._agent.run(query)
            log_agent_response(
                self._agent_card.name, "Task completed successfully", context_id
            )
            log_agent_response(self._agent_card.name, "content", response.output)

            return {
                "is_task_complete": True,
                "require_user_input": False,
                "content": response.output,
            }
        except Exception as exc:  # noqa: BLE001
            error_msg = f"Error during invoke: {exc}"
            log_error(error_msg)
            return {
                "is_task_complete": False,
                "require_user_input": True,
                "content": f"Error: {exc}",
            }

    async def stream(
        self, query: str, context_id: str
    ) -> AsyncGenerator[ResponsePayload, None]:
        """Yield incremental updates while the agent processes *query*."""

        try:
            log_agent_request(self._agent_card.name, query, context_id)

            # Initial placeholder so the caller can display progress feedback
            log_agent_activity(self._agent_card.name, "Starting request processing")
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Processing your request...",
            }
            log_agent_activity(self._agent_card.name, "Sending request to OpenAI")
            response = await self._agent.run(query)
            log_agent_activity(self._agent_card.name, "Received response from OpenAI")

            # Final message
            log_agent_response(
                self._agent_card.name, "Task completed successfully", context_id
            )
            log_agent_response(self._agent_card.name, "content", response.output)
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": response.output,
            }

        except Exception as exc:
            error_msg = f"Error during processing: {exc}"
            log_error(error_msg)
            yield {
                "is_task_complete": False,
                "require_user_input": True,
                "content": f"Error: {exc}",
            }


class PydanticAIAgentExecutor(AgentExecutor):
    """Simple executor for the OpenAI Agent."""

    def __init__(self, pydantic_ai_agent: PydanticAIAgentWrapper):
        self.agent = pydantic_ai_agent
        log_agent_activity(self.agent._agent_card.name, "Initialized")

    async def execute(self, context, event_queue):
        """Execute the agent."""
        log_agent_activity(self.agent._agent_card.name, "Starting execution")
        query = context.get_user_input()
        log_agent_activity(
            self.agent._agent_card.name,
            f"Received execution request for context: {context.message.context_id}",
        )
        log_agent_activity(self.agent._agent_card.name, f"Query: {query}")

        task = context.current_task or new_task(context.message)
        await event_queue.enqueue_event(task)
        log_agent_activity(self.agent._agent_card.name, f"Created new task: {task.id}")

        updater = TaskUpdater(event_queue, task.id, task.context_id)
        log_agent_activity(self.agent._agent_card.name, "Created task updater")

        try:
            log_agent_activity(self.agent._agent_card.name, "Starting agent stream")
            async for item in self.agent.stream(query, task.context_id):
                log_agent_activity(
                    self.agent._agent_card.name, f"Received stream item: {item}"
                )
                is_task_complete = item["is_task_complete"]
                require_user_input = item["require_user_input"]
                content = item["content"]

                message = new_agent_text_message(content, task.context_id, task.id)

                if is_task_complete:
                    log_agent_activity(
                        self.agent._agent_card.name, f"Task {task.id} completed"
                    )
                    await updater.complete(message)
                elif require_user_input:
                    log_agent_activity(
                        self.agent._agent_card.name,
                        f"Task {task.id} requires user input",
                    )
                    await updater.update_status(TaskState.input_required, message)
                else:
                    log_agent_activity(
                        self.agent._agent_card.name, f"Task {task.id} in progress"
                    )
                    await updater.update_status(TaskState.working, message)

        except Exception as e:
            from a2a.utils.errors import ServerError
            from a2a.types import InternalError

            log_error(f"Error in executor: {str(e)}")
            log_error(f"Error details: {type(e).__name__}")
            raise ServerError(error=InternalError()) from e

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("cancel not supported")
