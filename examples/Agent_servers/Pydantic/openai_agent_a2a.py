
import dotenv
from pydantic_ai import Agent
from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from isek.utils.common import log_agent_start, log_system_event
from isek.node.node_v3_a2a import Node
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
    app = Node.create_server(agent_executor, agent_card)
    node.build_server(app, name="OpenAI Agent", daemon=False)

if __name__ == "__main__":
    # TODO
    main()
