import os
import asyncio
from uuid import uuid4

import dotenv

from isek.node.node_v3_a2a import Node
from isek.utils.common import log_agent_request
from isek.utils.common import log_agent_response
from isek.utils.common import log_system_event

dotenv.load_dotenv()

AGENT_CARDS_DIR = 'agent_cards'
MODEL = 'text-embedding-ada-002'

# Target agent HTTP URL (used when p2p is disabled)
agent_url = 'http://localhost:9999'


AGENT_CARD_WELL_KNOWN_PATH = "/.well-known/agent.json"  # kept for compatibility

async def query_agent(query: str) -> str:
    """Execute a task on a remote agent and return the aggregated response.

    Args:
        query: The query to send to the agent.

    Returns:
        str: The content of the task result.
    """
        # Fallback to direct HTTP using the Node/A2A client
    node = Node(host="127.0.0.1", port=8888, node_id="a2a-client")
    log_agent_request("a2a-client", f"Executing task on {agent_url} with query: {query}")
    message_content = await node.send_message(agent_url, query)
    log_agent_response("a2a-client", f"Task result content: {message_content}")

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
    log_system_event("[get_agent_card]", f"Fetching agent card from {agent_url}")
    card = await node.get_agent_card_by_url(agent_url)
    log_system_event("[get_agent_card]", f"Received agent card: {card}")
    return card


# Example usage
print(asyncio.run(query_agent("Hello, how are you?")))


