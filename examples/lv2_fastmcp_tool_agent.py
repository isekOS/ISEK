from isek.agent.isek_agent import IsekAgent
from isek.models.openai import OpenAIModel
from isek.tools.fastmcp_toolkit import FastMCPToolkit
import dotenv
import os

dotenv.load_dotenv()

def main():
    """Example agent using FastMCP toolkit"""
    
    # Get GitHub token
    github_token = os.getenv("GITHUB_TOKEN")
    
    if not github_token:
        print("⚠️  Warning: GITHUB_TOKEN not set")
        print("Please set GITHUB_TOKEN environment variable for GitHub Copilot MCP")
        return
    else:
        print("✅ Using FastMCP toolkit with GitHub Copilot")
        try:
            # Use the pre-created fastmcp_tools instance
            mcp_tools = FastMCPToolkit(
                server_source="https://api.githubcopilot.com/mcp/",
                name="github_fastmcp",
                auth_token=github_token,
                debug=True,
            )
            
            # Check connection status
            if mcp_tools.health_check():
                print("✅ FastMCP connection successful")
                available_tools = mcp_tools.list_available_tools()
                print(f"Found {len(available_tools)} MCP tools")
            else:
                print("❌ FastMCP connection failed")
                return
        except Exception as e:
            print(f"❌ FastMCP toolkit creation failed: {e}")
            return

    print("=== Available tools ===")
    tools = mcp_tools.list_available_tools()
    for tool in tools:
        print(f"- {tool}")

    # Create Agent
    agent = IsekAgent(
        name="FastMCP Assistant",
        model=OpenAIModel(model_id="gpt-4o-mini"),
        tools=[mcp_tools],
        description="An intelligent assistant with FastMCP tool access",
        instructions=[
            "Be helpful and informative",
            "Use FastMCP tools when appropriate",
            "Provide accurate information",
            "Explain concepts clearly"
        ],
        success_criteria="User gets helpful responses with appropriate tool usage",
        debug_mode=True
    )

    print("=== FastMCP Assistant Ready ===")
    
    # Test conversations
    test_queries = [
        "Hello! What can you help me with?",
        "Can you search for Python machine learning repositories?"
    ]
    
    for query in test_queries:
        # print(f"\n🤖 User: {query}")
        # response = agent.run(query)
        # print(f"🤖 Assistant: {response}")
        # print("-" * 50)
        agent.print_response(query)

if __name__ == "__main__":
    main() 