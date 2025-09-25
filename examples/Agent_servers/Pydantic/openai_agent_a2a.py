
import asyncio
from typing import Any, AsyncGenerator
import os
import dotenv
from pydantic_ai import Agent
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState, AgentCard, AgentCapabilities, AgentSkill
from a2a.utils import new_agent_text_message, new_task
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from isek.utils.common import (
    log_agent_start,
    log_agent_activity,
    log_agent_request,
    log_agent_response,
    log_error,
    log_system_event
)
from isek.node.node_v3_a2a import Node
from a2a.server.agent_execution.agent_executor import AgentExecutor

dotenv.load_dotenv()

agent_card = AgentCard(
    name="OpenAI Agent",
    url="http://localhost:9999",
    description="Simple OpenAI GPT-4 wrapper agent",
    version="1.0",
    capabilities=AgentCapabilities(
        streaming=True,
        tools=True,  # Enable tools support
        task_execution=True  # Enable task execution
    ),
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
    skills=[
        AgentSkill(
            id="general_assistant",
            name="General Assistant",
            description="Provides helpful responses to general queries using GPT-4",
            tags=["general", "assistant", "gpt4"],
            examples=[
                "What is machine learning?",
                "How do I write a Python function?",
                "Explain quantum computing"
            ]
        )
    ]
)

class OpenAIAgent:
    """Simple OpenAI wrapper agent."""
    
    def __init__(self):
        """Initialize the OpenAI agent with a basic configuration."""
        self.agent = Agent(
            model="gpt-4",
            system_prompt="You are a helpful AI assistant that provides clear and concise responses."
        )
        log_agent_activity("OpenAI Agent", "Initialized with GPT-4 model")

    async def stream(self, query: str, contextId: str) -> AsyncGenerator[dict[str, Any], None]:
        """Stream the agent response."""
        try:
            log_agent_request("OpenAI Agent", query, contextId)
            
            # Initial message
            log_agent_activity("OpenAI Agent", "Starting request processing")
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Processing your request...",
            }

            # Get response from OpenAI
            log_agent_activity("OpenAI Agent", "Sending request to OpenAI")
            response = await self.agent.run(query)
            log_agent_activity("OpenAI Agent", "Received response from OpenAI")

            # Return final response
            log_agent_response("OpenAI Agent", "Task completed successfully", contextId)
            log_agent_response("OpenAI Agent", "content", response.output)
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": response.output,
            }

        except Exception as e:
            error_msg = f"Error during processing: {str(e)}"
            log_error(error_msg)
            yield {
                "is_task_complete": False,
                "require_user_input": True,
                "content": f"Error: {str(e)}",
            }

class OpenAIAgentExecutor(AgentExecutor):
    """Simple executor for the OpenAI Agent."""

    def __init__(self):
        self.agent = OpenAIAgent()
        log_agent_activity("OpenAI Agent Executor", "Initialized")

    async def execute(self, context, event_queue):
        """Execute the agent."""
        log_agent_activity("OpenAI Agent Executor", "Starting execution")
        query = context.get_user_input()
        log_agent_activity("OpenAI Agent Executor", f"Received execution request for context: {context.message.contextId}")
        log_agent_activity("OpenAI Agent Executor", f"Query: {query}")
        
        task = context.current_task or new_task(context.message)
        await event_queue.enqueue_event(task)
        log_agent_activity("OpenAI Agent Executor", f"Created new task: {task.id}")
        
        updater = TaskUpdater(event_queue, task.id, task.contextId)
        log_agent_activity("OpenAI Agent Executor", "Created task updater")

        try:
            log_agent_activity("OpenAI Agent Executor", "Starting agent stream")
            async for item in self.agent.stream(query, task.contextId):
                log_agent_activity("OpenAI Agent Executor", f"Received stream item: {item}")
                is_task_complete = item["is_task_complete"]
                require_user_input = item["require_user_input"]
                content = item["content"]

                message = new_agent_text_message(content, task.contextId, task.id)

                if is_task_complete:
                    log_agent_activity("OpenAI Agent Executor", f"Task {task.id} completed")
                    await updater.complete(message)
                elif require_user_input:
                    log_agent_activity("OpenAI Agent Executor", f"Task {task.id} requires user input")
                    await updater.update_status(TaskState.input_required, message, final=True)
                else:
                    log_agent_activity("OpenAI Agent Executor", f"Task {task.id} in progress")
                    await updater.update_status(TaskState.working, message)

        except Exception as e:
            from a2a.utils.errors import ServerError
            from a2a.types import InternalError
            log_error(f"Error in executor: {str(e)}")
            log_error(f"Error details: {type(e).__name__}")
            raise ServerError(error=InternalError()) from e
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("cancel not supported")

def main():
    """Run the OpenAI agent server."""
    log_agent_start("OpenAI Agent", 9999)
    node = Node(host="127.0.0.1", port=9999, node_id="openai-agent")
    app = Node.create_server(OpenAIAgentExecutor(), agent_card)
    node.build_server(app, name="OpenAI Agent", daemon=False)

if __name__ == "__main__":
    main()
