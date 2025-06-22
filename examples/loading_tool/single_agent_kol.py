import time
import os
from isek.agent.single_agent import SingleAgent
from isek.models.openai.chat import OpenAIModel
from isek.agent.persona import Persona
from dotenv import load_dotenv

load_dotenv()


model = OpenAIModel(api_key=os.environ.get("OPENAI_API_KEY"))
knowledge_base = {}


def publish_twitter(content: str) -> str:
    return "twitter content published: " + content


def get_news(query: str) -> str:
    query_result = model.generate_text("get news about " + query)
    print(query_result)
    return "news: " + query_result


def save_knowledge(query: str, answer: str) -> str:
    knowledge_base[query] = answer
    return "knowledge saved"


def get_knowledge(query: str) -> str:
    return str(knowledge_base)


Agent_info = {
    "name": "chris",
    "bio": "An experienced crypto currency trader",
    "lore": "Your mission is to assist user with crypto related questions",
    "knowledge": "crypto news, crypto trading strategies, crypto market analysis",
    "routine": [
        "if user ask about crypto news, provide the latest news",
        "if user ask about coin recommendation, provide the coin names",
        "if user ask about trading strategies, provide the best strategies",
        "if user ask about market analysis, provide the latest market analysis",
        "if user ask about other topics, reject the task",
        "always respond to user with concise answers, less than 4 sentences",
        "if manager agent ask you to promote a product, use your social media ability to promote it"
        "if no input or heartbeat mode, you can decide either collect news or promote product",
    ],
}
Agent = Persona.from_json(Agent_info)


def main():
    sylana_agent = SingleAgent(model=model, persona=Agent)
    sylana_agent.tool_manager.register_tools(
        [publish_twitter, get_news, save_knowledge, get_knowledge]
    )
    time.sleep(2)
    sylana_agent.run_cli()
    # what is the chance of picking 4 cards and they are 4 Ace in ca
    # rd game


if __name__ == "__main__":
    main()
