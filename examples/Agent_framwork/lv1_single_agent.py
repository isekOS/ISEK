from isek.agent.isek_agent import IsekAgent
from isek.models.openai.openai import OpenAIModel
from isek.utils.log import LoggerManager
from isek.models.base import SimpleMessage
import dotenv
dotenv.load_dotenv()
LoggerManager.plain_mode()


agent = IsekAgent(
    name="Email Polisher",
    model=OpenAIModel(),
    description="A specialized agent that helps polish and improve email content. I can help with grammar, tone, clarity, professionalism, and overall effectiveness of email communications. I provide suggestions for better structure, word choice, and formatting to make emails more impactful and professional.",
)

# Test email to polish
test_email = """
I wanted to reach out to my boss about the project we discussed last week. I think we should meet to talk about the next steps and see what we can do to move forward.
"""

# response = agent.run(f"Please polish this email to make it more professional and effective:\n\n{test_email}")
# response = agent.run(test_email)
# print(response)
response = agent.print_response(test_email)
