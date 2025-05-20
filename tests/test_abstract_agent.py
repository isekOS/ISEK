import pytest
from unittest.mock import Mock
from isek.agent.abstract_agent import AbstractAgent

class TestAgent(AbstractAgent):
    def build(self, daemon=False):
        pass

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
    return TestAgent(model=mock_model)

def test_agent_response(agent):
    """Test basic response"""
    response = agent.response("Hello")
    assert isinstance(response, str)
    assert agent.model.create.called

def test_agent_tool(mock_model):
    """Test basic tool usage"""
    def test_tool(arg):
        return f"Result: {arg}"
    
    agent = TestAgent(model=mock_model)
    agent.tool_manager.register_tool(test_tool)
    assert "test_tool" in agent.tool_manager.get_tool_names()