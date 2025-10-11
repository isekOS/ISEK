import os
import asyncio
from uuid import uuid4

import dotenv

from isek.node.node_v3_a2a import Node
from isek.protocol.a2a_protocol_v2 import A2AProtocolV2
from isek.utils.common import log_system_event

dotenv.load_dotenv()

AGENT_CARDS_DIR = 'agent_cards'
MODEL = 'text-embedding-ada-002'

# Peer ID of the agent server - copy it from the server's output
#TODO make it configurable
server_peer_id = '12D3KooWNxWoUFmXXFBE65b99pfwMsW1yWWJmpKMbkiVRjCNERSb'
AGENT_CARD_WELL_KNOWN_PATH = "/.well-known/agent.json"  # kept for compatibility

async def query_agent(query: str) -> str:
    """Execute a task on a remote agent and return the aggregated response.

    Args:
        query: The query to send to the agent.

    Returns:
        str: The content of the task result.
    """
    p2p = A2AProtocolV2(
        host="127.0.0.1", 
        port=8888, 
        p2p_enabled=True, 
        p2p_server_port=9002,
        relay_ip="155.138.145.190",
        relay_peer_id="12D3KooWShd5s1ziziZNkiqN56XVpWH3chZHeq7EeSzHKMzR12vf"
    )
    p2p.start_p2p_server(wait_until_ready=True)
    log_system_event("[p2p] client", f"peer_id={p2p.peer_id}")
    log_system_event("[p2p] client", f"p2p_address={p2p.p2p_address}")

    # Use local p2p bridge HTTP to call the remote peer
    log_system_event("[p2p] client", f"Sending message to peer {server_peer_id}")
    log_system_event("[p2p] client", f"Query: {query}")
    
    resp = p2p.send_message(
        sender_node_id="a2a-client",
        receiver_peer_id=server_peer_id,
        message=query,
    )
    log_system_event("[p2p] client", f"Response: {resp}")
    # Parse standard A2A JSON-RPC response
    message_content = None
    try:
        status = resp.get("result", {}).get("status")
        if isinstance(status, dict) and "message" in status:
            message_content = status["message"]
    except Exception:
        pass
    if message_content is None:
        try:
            parts = resp.get("result", {}).get("parts", [])
            if parts and isinstance(parts[0], dict) and "text" in parts[0]:
                message_content = parts[0]["text"]
        except Exception:
            pass
    if message_content is None:
        message_content = str(resp)
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
# print(asyncio.run(get_agent_card(agent_urls[0])))


