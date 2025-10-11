from isek.agent.isek_agent import IsekAgent
from isek.models.openai.openai import OpenAIModel
from isek.memory.memory import Memory
from isek.tools.calculator import calculator_tools
from isek.tools.toolkit import Toolkit
from isek.team.isek_team import IsekTeam
import dotenv
import os

dotenv.load_dotenv()

# Set up models
researcher_model = OpenAIModel()
writer_model = OpenAIModel()
team_model = OpenAIModel()

# Set up memory for each agent
researcher_memory = Memory()
writer_memory = Memory()

# Set up toolkits
researcher_toolkit = calculator_tools
writer_toolkit = Toolkit(tools=[])

# Create team members (agents)
agent1 = IsekAgent(
    name="Researcher",
    description="Expert in research and analysis. Can use tools to calculate or retrieve data.",
    model=researcher_model,
    memory=researcher_memory,
    tools=[researcher_toolkit]
)
agent2 = IsekAgent(
    name="Writer",
    description="Expert in writing and communication. Summarizes and presents information clearly.",
    model=writer_model,
    memory=writer_memory,
    tools=[writer_toolkit]
)

# Create the team
team = IsekTeam(
    name="AI Research Team",
    members=[agent1, agent2],
    model=team_model,
    mode="coordinate",  # Try also "route" or "collaborate"
    description="A team that researches the latest AI developments and writes comprehensive reports."
)

# Run the team on a complex task
task = (
    "Research the latest advancements in AI, "
    "calculate the average number of new AI papers published per month in 2023, "
    "and write a concise summary for a general audience."
)
team.print_response(task)


# response = team.run(task)
# print("Team Response:\n", response)
