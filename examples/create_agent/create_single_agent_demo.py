import sys
import os
from isek.agent.single_agent import SingleAgent
from isek.agent.persona import Persona
from isek.models.openai.chat import OpenAIModel
from isek.models.litellm.chat import LiteLLM
from dotenv import load_dotenv


def publish_content(platform="twitter", content=""):
    return "content published on" + platform

def fast_create():
    load_dotenv()
    return SingleAgent()


def statement_llm_create():
    load_dotenv()
    model = LiteLLM(
        provider="openai",
        model_name=os.environ["OPENAI_MODEL_NAME"],
        base_url=os.environ["OPENAI_BASE_URL"],
        api_key=os.environ["OPENAI_API_KEY"],
    )
    return SingleAgent(model=model)


def custom_create():
    # create your persona
    persona_desc = {
        "name": "Custom Agent",
        "bio": "An agent for testing",
        "lore": "Be responsible for helping users conduct agent testing",
        "knowledge": "",
        "routine": "",
    }
    persona = Persona.from_json(persona_desc)
    # create your llm
    load_dotenv()
    model = LLM(
        provider="openai",
        model_name=os.environ["OPENAI_MODEL_NAME"],
        base_url=os.environ["OPENAI_BASE_URL"],
        api_key=os.environ["OPENAI_API_KEY"],
    )
    agent = SingleAgent(persona=persona, model=model)
    agent.tool_manager.register_tools([publish_content])
    return agent
 
def create_anthropic_agent():
    # create your persona
    persona_desc = {
        "name": "Anthropic Agent",
        "bio": "An agent for testing with Anthropic",
        "lore": "Be responsible for helping users conduct agent testing with Anthropic",
        "knowledge": "",
        "routine": "",
    }
    persona = Persona.from_json(persona_desc)
    # create your llm
    load_dotenv()
    model = LLM(
        provider="anthropic",
        model_name=os.environ["ANTHROPIC_MODEL_NAME"],
        api_key=os.environ["ANTHROPIC_API_KEY"],
    )
    agent = SingleAgent(persona=persona, model=model)
    agent.tool_manager.register_tools([publish_content])
    return agent

def create_gemini_agent():
    # create your persona
    persona_desc = {
        "name": "Gemini Agent",
        "bio": "An agent for testing with Gemini",
        "lore": "Be responsible for helping users conduct agent testing with Gemini",
        "knowledge": "",
        "routine": "",
    }
    persona = Persona.from_json(persona_desc)
    # create your llm
    load_dotenv()
    model = LLM(
        provider="gemini",
        model_name=os.environ.get("GEMINI_MODEL_NAME", "gemini-2.0-flash"),
        api_key=os.environ["GEMINI_API_KEY"],
    )
    agent = SingleAgent(persona=persona, model=model)
    agent.tool_manager.register_tools([publish_content])
    return agent

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "fast_create"
    if mode == "statement_llm_create":
        agent = statement_llm_create()
    elif mode == "custom_create":
        agent = custom_create()
    elif mode == "anthropic_create":
        agent = create_anthropic_agent()
    elif mode == "gemini_create":
        agent = create_gemini_agent()
    else:
        agent = fast_create()
    agent.run("Hello! please publish your introduction on X")