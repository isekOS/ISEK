import httpx
import json
from pathlib import Path
import asyncio
from a2a.client import A2AClient
from a2a.types import (
    AgentCard,
    Message,
    MessageSendParams,
    Part,
    Role,
    SendMessageRequest,
    TextPart,
    JSONRPCErrorResponse,
)
from mcp.server.fastmcp.utilities.logging import get_logger
from uuid import uuid4
import dotenv

dotenv.load_dotenv()

logger = get_logger(__name__)
AGENT_CARDS_DIR = 'agent_cards'
MODEL = 'text-embedding-ada-002'
agent_urls = ['http://localhost:9999', # openai agent
              'http://localhost:10020', # trending agent
              'http://localhost:10021' # analyzer agent
            ]
AGENT_CARD_WELL_KNOWN_PATH = "/.well-known/agent.json"

async def get_agent_card_by_url(agent_url: str) -> dict:
    """Fetch and cache agent cards from all configured agent URLs.

    The function uses a simple in-memory cache (``_agent_info_cache``) to avoid
    fetching the ­same agent card repeatedly.  If a card is not cached, it is
    retrieved from the agent’s “well-known” endpoint and stored in the cache.
    
    Args:
        agent_url: The URL of the agent to fetch the agent card from.

    Returns:
        dict: ``AgentCard`` fully JSON-serialisable object for interoperability with the rest of the MCP pipeline.
    """
    timeout_config = httpx.Timeout(10.0)  # seconds
    logger.debug("[get_agent_card_by_url],Fetching agent card for %s", agent_url)
    async with httpx.AsyncClient(timeout=timeout_config) as httpx_client:
        response = await httpx_client.get(f"{agent_url}{AGENT_CARD_WELL_KNOWN_PATH}")
        response.raise_for_status()
        card_data = response.json()
        return card_data

async def main(query: str) -> str:
    """Execute a task on a remote agent and return the aggregated response.

    Args:
        query: The query to send to the agent.

    Returns:
        str: The content of the task result.
    """
    # Fetch the agent-card data and build a proper ``AgentCard`` instance.
    agent_card_data = await get_agent_card_by_url(agent_urls[0])
    agent_card = AgentCard(**agent_card_data)

    logger.info("[execute_task],Executing task on agent %s with query: %s", agent_card.name, query)

    # Build request params
    msg_params = MessageSendParams(
        message=Message(
            role=Role.user,
            parts=[Part(TextPart(text=query))],
            messageId=uuid4().hex  # Add this line to include the required messageId field
        )
    )

    logger.debug("[execute_task] Sending non-streaming request …")
    timeout_config = httpx.Timeout(10.0)
    async with httpx.AsyncClient(timeout=timeout_config) as httpx_client:
        client = A2AClient(httpx_client, agent_card=agent_card)
        response = await client.send_message(
            SendMessageRequest(id=str(uuid4().hex), params=msg_params)
        )
        
        if isinstance(response, JSONRPCErrorResponse):
            logger.error("[execute_task] Error response received: %s", response)
            return "Error: Unable to execute task"

        message_content = response.root.result.status.message

        logger.info("[execute_task] Task result content: %s", message_content)

        return message_content

# Example usage
print(asyncio.run(main("Hello, how are you?")))
