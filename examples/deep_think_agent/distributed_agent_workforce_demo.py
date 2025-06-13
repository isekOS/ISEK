import time
import os
import numpy as np
from isek.agent.distributed_agent import DistributedAgent
from isek.node.isek_center_registry import IsekCenterRegistry
from isek.agent.persona import Persona
from isek.util.logger import logger
from isek.llm import OpenAIModel
from isek.llm.llm import LLM
from dotenv import load_dotenv


def publish_content(platform="twitter", content=""):
    logger.info(f"[]published content on {platform}: {content}")
    return "content published on" + platform


def image_gen(input=""):
    logger.info("[]image generated")
    return "image generated with id" + str(np.random.randint(100))


def main():
    # registry = EtcdRegistry(host=os.environ["ISEK_ETCD_IP"], port=os.environ["ISEK_ETCD_PORT"])

    # run local registry using
    # python isek_center.py
    # pip install isek
    # how to?
    # isek run registry

    load_dotenv()
    registry = IsekCenterRegistry()
    Mani_info = {
        "name": "Mani",
        "bio": "An experienced manager",
        "lore": "Your mission is to manage the team",
        "knowledge": "recruit, assign tasks, manage tasks, manage projects",
        "routine": "1. if receive a task, decompose the task to subtasks. 2. search for partners for each task. 3. send message to other agnet to do the tasks. user is your boss, do not ask user to do the task",
    }

    Eddie_info = {
        "name": "Eddie",
        "bio": "An experienced photo designer",
        "lore": "Your mission is to generate beautiful photos based on clients' requirements",
        "knowledge": "photo editing, photo design, photo retouching",
        "routine": "",
    }
    Infy_info = {
        "name": "Infy",
        "bio": "An experienced influencer",
        "lore": "Your mission is to operate social media accounts and generate traffic",
        "knowledge": "social media, social media marketing, social media management",
        "routine": "you are responsiable for publish content on twitter, facebook, and instagram",
    }

    # model = OpenAIModel(
    #     model_name=os.environ.get("OPENAI_MODEL_NAME"),
    #     base_url=os.environ.get("OPENAI_BASE_URL"),
    #     api_key=os.environ.get("OPENAI_API_KEY"),
    # )
    model = LLM(
        provider="gemini",
        model_name=os.environ.get("GEMINI_MODEL_NAME", "gemini-2.0-flash"),
        api_key=os.environ["GEMINI_API_KEY"],
    )

    Mani = Persona.from_json(Mani_info)
    Eddie = Persona.from_json(Eddie_info)
    Infy = Persona.from_json(Infy_info)

    Mani_agent = DistributedAgent(
        persona=Mani, host="localhost", port=8080, registry=registry, model=model
    )
    Mani_agent.tool_manager.register_tools(
        [
            Mani_agent.search_partners,
            Mani_agent.send_message,
            Mani_agent.decompose_task,
        ]
    )
    Mani_agent.build(daemon=True)

    Eddie_agent = DistributedAgent(
        persona=Eddie, host="localhost", port=8081, registry=registry, model=model
    )
    Eddie_agent.tool_manager.register_tools(
        [
            image_gen,
            Eddie_agent.search_partners,
            Eddie_agent.send_message,
        ]
    )
    Eddie_agent.build(daemon=True)

    Infy_agent = DistributedAgent(
        persona=Infy, host="localhost", port=8082, registry=registry, model=model
    )
    Infy_agent.tool_manager.register_tools(
        [
            publish_content,
        ]
    )
    Infy_agent.build(daemon=True)

    time.sleep(2)
    # Mani_agent.run("I want to promote my shoes product with a budget of $100")

    Mani_agent.run_cli()


if __name__ == "__main__":
    # LoggerManager.init(debug=True)
    main()
