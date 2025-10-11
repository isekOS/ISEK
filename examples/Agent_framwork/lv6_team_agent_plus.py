from isek.agent.isek_agent import IsekAgent
from isek.models.openai.openai import OpenAIModel
from isek.memory.memory import Memory
from isek.tools.calculator import calculator_tools
from isek.tools.toolkit import Toolkit
from isek.team.isek_team import IsekTeam
from isek.utils.print_utils import print_panel
import dotenv
import os

dotenv.load_dotenv()

def test_team_modes():
    """Test different team modes to demonstrate their capabilities."""
    print_panel(title="Testing Team Modes (Coordination Model)", color="yellow")

    # Set up models
    researcher_model = OpenAIModel()
    writer_model = OpenAIModel()
    team_model = OpenAIModel()

    # Set up memory for each agent
    researcher_memory = Memory()
    writer_memory = Memory()

    # Set up toolkits
    researcher_toolkit = calculator_tools  # calculator_tools is already a Toolkit
    writer_toolkit = Toolkit(tools=[])  # Writer has no tools in this example

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

    # Test different team modes
    modes = ["coordinate", "route", "collaborate"]
    
    for mode in modes:
        # Run the team on a task
        task = (
            "Calculate 15 * 23 and then write a brief explanation of what this calculation represents."
        )
        print_panel(title=f"Testing Team Mode: {mode.upper()}", content=f"Task: {task}", color="bright_blue")
        # print(f"\n{'='*60}")
        # print(f"Testing Team Mode: {mode.upper()}")
        # print(f"{'='*60}")
        
        # Create the team with current mode
        team = IsekTeam(
            name=f"AI Research Team ({mode})",
            members=[agent1, agent2],
            model=team_model,
            mode=mode,
            description="A team that researches the latest AI developments and writes comprehensive reports.",
            debug_mode=True  # Enable debug to see what's happening
        )

        response = team.run(task)
        print_panel(title="Response", content=response)
        # print(f"Response:\n{response}")
        # print("-" * 40)

def test_simple_team():
    """Test a simple team without coordination model."""

    print_panel(title="Testing Simple Team (No Coordination Model)", color="yellow")

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

    # Create the team without a coordination model
    team = IsekTeam(
        name="Simple Research Team",
        members=[agent1, agent2],
        model=team_model,
        mode="coordinate",  # Will use simple coordination since no model
        description="A simple team that researches and writes reports.",
        debug_mode=True
    )

    # Run the team on a task
    task = "Calculate 10 + 5 and explain what this means."

    team.print_response(task)
    

if __name__ == "__main__":

    print_panel(title="ISEK Team Agent Demo", content="Testing different team modes and configurations...", color="bright_yellow")

    # Test simple team first
    test_simple_team()
    
    # Test different team modes
    test_team_modes()
    print_panel(title="ISEK Team Agent Demo", content="Demo completed!", color="bright_yellow")
