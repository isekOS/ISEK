
import dotenv
from pydantic_ai import Agent
from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from isek.utils.common import log_agent_start, log_system_event
from isek.node.node_v3_a2a import Node
from isek.protocol.a2a_protocol_v2 import A2AProtocolV2
from isek.adapter.pydantic_ai_adapter import PydanticAIAgentWrapper,PydanticAIAgentExecutor
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

my_agent=Agent(
    model="gpt-4",
    system_prompt="You are a helpful AI assistant that provides clear and concise responses."
)

wrapper = PydanticAIAgentWrapper(my_agent, agent_card)
agent_executor = PydanticAIAgentExecutor(wrapper)

def main():
    """Run the OpenAI agent server."""
    log_agent_start("OpenAI Agent", 9999)
    node = Node(host="127.0.0.1", port=9999, node_id="openai-agent")


    # P2P connection start =====================================================
    # Optional: start p2p bridge for this server so that clients can reach it via p2p
    # The p2p bridge will forward inbound requests to the local agent HTTP server at port 9999
    p2p = A2AProtocolV2(
        host="127.0.0.1", 
        port=9999, 
        p2p_enabled=True, 
        p2p_server_port=9001,
        relay_ip="155.138.145.190",
        relay_peer_id="12D3KooWAom1Up6ZmpWgCSZGU5miehN5j2fczRNaiPUU4ZqmSCJq"
    )
    # Run blocking wait so we can print the peer address before starting the agent server
    p2p.start_p2p_server(wait_until_ready=True)
    log_system_event("[p2p] server", f"peer_id={p2p.peer_id}")
    log_system_event("[p2p] server", f"p2p_address={p2p.p2p_address}")
    # P2P connection end =======================================================
    
    
    app = Node.create_server(agent_executor, agent_card)
    node.build_server(app, name="OpenAI Agent", daemon=False)

if __name__ == "__main__":
    # TODO
    main()
