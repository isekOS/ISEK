from isek.agent.isek_agent import IsekAgent
from isek.models.openai import OpenAIModel
from isek.memory.memory import Memory
from isek.tools.calculator import calculator_tools
from isek.models.base import SimpleMessage
from isek.utils.print_utils import print_panel
import dotenv
dotenv.load_dotenv()

# Create memory instance
memory = Memory(debug_mode=True)

# Create agent with memory and tools
agent = IsekAgent(
    name="Memory Tool Agent",
    model=OpenAIModel(),
    memory=memory,
    tools=[calculator_tools],
    description="A helpful assistant with memory and calculator abilities",
    instructions=["Be polite", "Provide accurate information", "Remember previous conversations", "Use tools for math questions when possible"],
    success_criteria="User gets a helpful response that takes into account previous interactions and includes math answers when needed",
    debug_mode=True
)

# Test conversation with memory
agent.print_response("Hello! My name is Alice.", user_id="alice", session_id="session1")
agent.print_response("What's my name?", user_id="alice", session_id="session1")
agent.print_response("What is 5 times 6? And what's my name?", user_id="alice", session_id="session1")
agent.print_response("Tell me about our previous conversations and calculate 10 + 15.", user_id="alice", session_id="session1")


# Show memory contents
total_memories = len(memory.get_user_memories('alice'))
print_panel(title=f"Memory Contents", content="", title_align="left")
for i, memory_item in enumerate(memory.get_user_memories('alice')):
    print_panel(title=f"Memory {i+1}/{total_memories}", content=str(memory_item.memory), title_align="left")

total_runs = len(memory.get_runs('session1'))
print_panel(title=f"Session runs", content="", title_align="left")
for i, run in enumerate(memory.get_runs('session1')):
    print_panel(title=f"Run {i + 1}/{total_runs}", content=f"{run}", title_align="left")