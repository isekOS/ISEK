import time
import os

from isek.agent.single_agent import SingleAgent
from isek.models.openai.chat import OpenAIModel
from isek.agent.persona import Persona
from dotenv import load_dotenv


def combination_calculator(n: str, k: str) -> str:
    # non-recursive implementation
    n = int(n)
    k = int(k)
    if k == 0:
        return "1"
    if k > n:
        return "0"
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return str(result)


def add(a: str, b: str) -> str:
    return str(int(a) + int(b))


def subtract(a: str, b: str) -> str:
    return str(int(a) - int(b))


def multiply(a: str, b: str) -> str:
    return str(int(a) * int(b))


def divide(a: str, b: str) -> str:
    return str(int(a) / int(b))


# model = OpenAIModel(
#     model_name="deepseek-chat",
#     base_url="https://api.deepseek.com",
#     api_key=os.environ.get("DEEPSEEK_API_KEY")
# )


def main():
    load_dotenv()

    model = OpenAIModel(
        model_name=os.environ.get("OPENAI_MODEL_NAME"),
        base_url=os.environ.get("OPENAI_BASE_URL"),
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    Eddie_info = {
        "name": "Eddie",
        "bio": "An experienced card game player",
        "lore": "Your mission is to assist user with card game related questions",
        "knowledge": "probability calculation, card game rules, card game strategies",
        "routine": "if you receive tasks that are not related to card game, reject the task",
    }

    Eddie = Persona.from_json(Eddie_info)

    eddie_agent = SingleAgent(model=model, persona=Eddie)
    eddie_agent.tool_manager.register_tools(
        [combination_calculator, add, subtract, multiply, divide]
    )
    time.sleep(2)
    eddie_agent.run_cli()
    # what is the chance of picking 4 cards and they are 4 Ace in card game


if __name__ == "__main__":
    main()
