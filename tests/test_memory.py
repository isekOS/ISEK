import pytest
from isek.agent.memory import AgentMemory

@pytest.fixture
def memory():
    return AgentMemory()

def test_store_memory_item(memory):
    """Test storing and retrieving memory items"""
    memory.store_memory_item("Test memory")
    items = memory.get_recent_memory_items()
    assert "Test memory" in items

def test_state_variables(memory):
    """Test state variable operations"""
    memory.set_state_variable("test_var", "test_value")
    assert memory.get_state_variable("test_var") == "test_value"
    
    all_vars = memory.get_all_state_variables()
    assert "test_var" in all_vars
    assert all_vars["test_var"] == "test_value"

def test_task_management(memory):
    """Test task creation and management"""
    task_id = memory.create_task("Test task")
    assert task_id in memory.get_all_tasks()
    
    memory.mark_task_completed(task_id)
    assert memory.get_all_tasks()[task_id]["completed"]

def test_knowledge_store(memory):
    """Test knowledge storage and retrieval"""
    memory.store_knowledge("test_topic", "test_content")
    content = memory.retrieve_knowledge("test_topic")
    assert content == "test_content"
    
    topics = memory.get_all_knowledge_topics()
    assert "test_topic" in topics