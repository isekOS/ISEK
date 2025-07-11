from isek.agent.isek_agent import IsekAgent
from isek.models.litellm import LiteLLMModel
from isek.models.base import SimpleMessage
from isek.tools.finance_toolkit.get_company_base_info import company_base_info_tools


import dotenv
dotenv.load_dotenv()

agent = IsekAgent(
    name="A-Share Company Info Agent",
    model=LiteLLMModel(provider = "deepseek", model_id="deepseek/deepseek-chat"),
    tools=[company_base_info_tools],
    description="An assistant that finds stock info and company info given a company name",
    instructions=["Be polite", 
                  "Always first retrieve a numeric stock code (e.g. '600519') and a company 'About' or official website URL base on the company name.",
                  "Then use the appropriate tool with the stock code to retrieve basic stock information.",
                  "If a valid 'About' or official website URL is available, use the appropriate tool to fetch additional company details and return it.",
                  "Always return concise and structured information.",
                  "Only make tool calls when needed.",
                  "If a valid stock code or official company URL cannot be found, inform the user explicitly and avoid making unnecessary tool calls."],
    success_criteria="User receives the correct stock info and basic company information for the given company name.",
    debug_mode=True
)

agent.print_response("hello")
agent.print_response("Give me the base info of Apple company, including its stock info and company info.")