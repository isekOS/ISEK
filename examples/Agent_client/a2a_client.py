import asyncio
from uuid import uuid4

import dotenv

from isek.node.node_v3_a2a import Node
from mcp.server.fastmcp.utilities.logging import get_logger
from isek.utils.log import log

dotenv.load_dotenv()

logger = get_logger(__name__)
AGENT_CARDS_DIR = 'agent_cards'
MODEL = 'text-embedding-ada-002'

agent_url = 'http://localhost:8000'

AGENT_CARD_WELL_KNOWN_PATH = "/.well-known/agent.json"  # kept for compatibility

async def query_agent(query: str) -> str:
    """Execute a task on a remote agent and return the aggregated response.

    Args:
        query: The query to send to the agent.

    Returns:
        str: The content of the task result.
    """
    # Instantiate a lightweight Node (acts as a client here)
    node = Node(host="127.0.0.1", port=8888, node_id="a2a-client")
    logger.info("[execute_task] Executing task on %s with query: %s",agent_url, query)
    message_content = await node.send_message(agent_url, query)
    logger.info("[execute_task] Task result content: %s", message_content)

    return message_content
async def get_agent_card(agent_url: str) -> dict:
    """
    Fetch the agent card from the given agent URL.

    Args:
        agent_url (str): The base URL of the agent.

    Returns:
        dict: The agent card as a dictionary.
    """
    node = Node(host="127.0.0.1", port=uuid4().int >> 112, node_id="a2a-client")
    logger.info("[get_agent_card] Fetching agent card from %s", agent_url)
    card = await node.get_agent_card_by_url(agent_url)
    logger.info("[get_agent_card] Received agent card: %s", card)
    return card


# Example usage
print(asyncio.run(query_agent("Hello, how are you?")))
# print(asyncio.run(get_agent_card(agent_urls[0])))


