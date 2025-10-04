
import dotenv
from pydantic_ai import Agent
from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from isek.utils.common import log_agent_start
from isek.node.node_v3_a2a_p2p import Node
import asyncio
import secrets
import multiaddr
import trio
from libp2p import new_host
from libp2p.crypto.secp256k1 import create_new_key_pair
import threading
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

async def main():
    node = Node(host="127.0.0.1", port=9999, node_id="openai-agent")
    app = Node.create_server(agent_executor, agent_card)
    node.build_server(app, name="OpenAI Agent", daemon=True)

    def trio_thread():
        async def run_p2p():
            key_pair = create_new_key_pair(secrets.token_bytes(32))
            host = new_host(key_pair=key_pair)
            listen_addr = multiaddr.Multiaddr("/ip4/0.0.0.0/tcp/8000")
            node.attach_p2p_host(host, protocol_id="/a2a/1.0.0")
            async with host.run(listen_addrs=[listen_addr]):
                await node.start_p2p_server(app)
                await trio.sleep_forever()
        trio.run(run_p2p)

    t = threading.Thread(target=trio_thread, daemon=True)
    t.start()

    # keep the asyncio program alive
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())