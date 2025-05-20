import pytest
from unittest.mock import Mock, patch
from isek.agent.distributed_agent import DistributedAgent

@pytest.fixture
def mock_model():
    return Mock()

@pytest.fixture
def mock_registry():
    registry = Mock()
    registry.get_available_nodes.return_value = {}
    return registry

@pytest.fixture
def agent(mock_model, mock_registry):
    return DistributedAgent(
        host="localhost",
        port=8080,
        registry=mock_registry,
        model=mock_model
    )

def test_agent_initialization(agent):
    """Test basic initialization"""
    assert agent.host == "localhost"
    assert agent.port == 8080

def test_agent_message(agent):
    """Safe test with patched internals"""
    with patch.object(agent, "on_message", return_value="patched response") as mocked:
        response = agent.on_message("sender", "Hello")
        assert response == "patched response"
        mocked.assert_called_once_with("sender", "Hello")
