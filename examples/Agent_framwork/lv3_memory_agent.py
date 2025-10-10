from isek.agent.isek_agent import IsekAgent
from isek.models.openai import OpenAIModel
from isek.memory.memory import Memory
from isek.models.base import SimpleMessage
from isek.utils.print_utils import print_panel
import dotenv
dotenv.load_dotenv()

# Create memory instance
memory = Memory(debug_mode=True)

# Create agent with memory
agent = IsekAgent(
    name="Memory Agent",
    model=OpenAIModel(),
    memory=memory,
    description="A helpful assistant with memory",
    instructions=["Be polite", "Provide accurate information", "Remember previous conversations"],
    success_criteria="User gets a helpful response that takes into account previous interactions",
    debug_mode=True
)

# # Test conversation with memory

agent.print_response("Hello! My name is Alice.", user_id="alice", session_id="session1")    
agent.print_response("What's my name?", user_id="alice", session_id="session1")
agent.print_response("Tell me about our previous conversations.", user_id="alice", session_id="session1")

# Show memory contents
total_memories = len(memory.get_user_memories('alice'))
print_panel(title=f"Memory Contents", content="", title_align="left")
for i, memory_item in enumerate(memory.get_user_memories('alice')):
    print_panel(title=f"Memory {i+1}/{total_memories}", content=str(memory_item.memory), title_align="left")

total_runs = len(memory.get_runs('session1'))
print_panel(title=f"Session runs", content="", title_align="left")
for i, run in enumerate(memory.get_runs('session1')):
    print_panel(title=f"Run {i + 1}/{total_runs}", content=f"{run}", title_align="left")


