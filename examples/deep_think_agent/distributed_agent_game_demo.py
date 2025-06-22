import time
import os
from isek.agent.distributed_agent import DistributedAgent
from isek.node.isek_center_registry import IsekCenterRegistry
from isek.agent.persona import Persona
from isek.models import OpenAIModel
from dotenv import load_dotenv


def main():
    load_dotenv()
    registry = IsekCenterRegistry()

    GM_info = {
        "name": "Game Master",
        "bio": "Game Master",
        "lore": "Your mission is to host the game and make sure the game is running smoothly",
        "knowledge": "game hosting",
        "routine": [
            "the game name is called coin donation",
            "the game rules are: 1. each player has 100 coins,",
            "2. each round, each player have to donate at least one coin to bank,",
            "3. the player donate the least coins to the bank has to donate 10 extra coins to the bank",
            "4, the player loses the game if he/she has no coins left",
            "5. the last player who has coins left wins the game",
            "your job is to host the game and make sure the game is running smoothly",
            "in the beginning of the game, you need to explain the game rules to each player",
            "you need to make sure each player knows the game rules",
            "in the beginig of each round, you need to ask each player how many coins they want to donate to the bank",
            "after each round, you need to check if any player has no coins left",
            "if any player has no coins left, you need to ask the player to leave the game",
        ],
    }
    P1_info = {
        "name": "Player One",
        "bio": "Game player",
        "lore": "Your mission is to win the game",
        "knowledge": "game theory",
        "routine": "",
    }
    P2_info = {
        "name": "Player Two",
        "bio": "Game player",
        "lore": "Your mission is to win the game",
        "knowledge": "game theory",
        "routine": "",
    }
    P3_info = {
        "name": "Player Three",
        "bio": "Game player",
        "lore": "Your mission is to win the game",
        "knowledge": "game theory",
        "routine": "",
    }
    P4_info = {
        "name": "Player Four",
        "bio": "Game player",
        "lore": "Your mission is to win the game",
        "knowledge": "game theory",
        "routine": "",
    }
    P5_info = {
        "name": "Player Five",
        "bio": "Game player",
        "lore": "Your mission is to win the game",
        "knowledge": "game theory",
        "routine": "",
    }
    model = OpenAIModel(
        model_name=os.environ.get("OPENAI_MODEL_NAME"),
        base_url=os.environ.get("OPENAI_BASE_URL"),
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    GM = Persona.from_json(GM_info)
    P1 = Persona.from_json(P1_info)
    P2 = Persona.from_json(P2_info)
    P3 = Persona.from_json(P3_info)
    P4 = Persona.from_json(P4_info)
    P5 = Persona.from_json(P5_info)

    GM_agent = DistributedAgent(
        persona=GM, host="localhost", port=8080, registry=registry, model=model
    )
    GM_agent.tool_manager.register_tools(
        [
            GM_agent.search_partners,
            GM_agent.send_message,
        ]
    )
    GM_agent.build(daemon=True)

    P1_agent = DistributedAgent(
        persona=P1, host="localhost", port=8081, registry=registry, model=model
    )
    P1_agent.tool_manager.register_tools(
        [
            P1_agent.send_message,
        ]
    )
    P1_agent.build(daemon=True)

    P2_agent = DistributedAgent(
        persona=P2, host="localhost", port=8082, registry=registry, model=model
    )
    P2_agent.tool_manager.register_tools(
        [
            P2_agent.send_message,
        ]
    )
    P2_agent.build(daemon=True)

    P3_agent = DistributedAgent(
        persona=P3, host="localhost", port=8083, registry=registry, model=model
    )
    P3_agent.tool_manager.register_tools(
        [
            P3_agent.send_message,
        ]
    )
    P3_agent.build(daemon=True)

    P4_agent = DistributedAgent(
        persona=P4, host="localhost", port=8084, registry=registry, model=model
    )
    P4_agent.tool_manager.register_tools(
        [
            P4_agent.send_message,
        ]
    )
    P4_agent.build(daemon=True)

    P5_agent = DistributedAgent(
        persona=P5, host="localhost", port=8085, registry=registry, model=model
    )
    P5_agent.tool_manager.register_tools(
        [
            P5_agent.send_message,
        ]
    )
    P5_agent.build(daemon=True)

    time.sleep(2)

    GM_agent.run("Start the game")
    # GM_agent.run_cli()


if __name__ == "__main__":
    # LoggerManager.init(debug=True)
    main()
