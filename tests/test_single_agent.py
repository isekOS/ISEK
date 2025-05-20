import pytest
from unittest.mock import Mock
from isek.agent.single_agent import SingleAgent

@pytest.fixture
def mock_model():
    message = Mock()
    message.content = "Test response"
    message.tool_calls = None
    
    choice = Mock()
    choice.message = message
    
    model = Mock()
    model.create.return_value = Mock(choices=[choice])
    return model

@pytest.fixture
def agent(mock_model):
    return SingleAgent(model=mock_model)

def test_agent_run(agent):
    """Test basic agent run"""
    response = agent.run("Hello")
    assert isinstance(response, str)
    assert agent.model.create.called

def test_agent_tool(mock_model):
    """Test agent with simple tool"""
    def test_tool(arg):
        return f"Result: {arg}"
    
    agent = SingleAgent(model=mock_model)
    agent.tool_manager.register_tool(test_tool)
    assert "test_tool" in agent.tool_manager.get_tool_names()