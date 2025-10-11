from isek.agent.isek_agent import IsekAgent
from isek.models.openai.openai import OpenAIModel
import dotenv
dotenv.load_dotenv()

agent = IsekAgent(name='MyAgent', model=OpenAIModel())
agent.print_response('Hello, world!')