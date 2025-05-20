import pytest
import json
from unittest.mock import Mock
from isek.agent.toolbox import ToolBox

@pytest.fixture
def toolbox():
    # Provide a persona with a name to avoid AttributeError when logging
    persona = Mock()
    persona.name = "TestPersona"
    return ToolBox(persona=persona)


def test_register_tool(toolbox):
    """Test tool registration"""
    def test_tool(arg: str) -> str:
        return f"Result: {arg}"
    
    toolbox.register_tool(test_tool)
    assert "test_tool" in toolbox.get_tool_names()


def test_tool_execution(toolbox):
    """Test tool execution"""
    def add(a: int, b: int) -> int:
        return a + b
    
    toolbox.register_tool(add)
    
    class ToolCall:
        def __init__(self):
            self.id = "test_id"
            self.function = Mock()
            self.function.name = "add"
            # arguments should be a JSON string
            self.function.arguments = json.dumps({"a": 1, "b": 2})
    
    result = toolbox.execute_tool_call(ToolCall())
    assert int(result) == 3


def test_get_tool_schemas(toolbox):
    """Test schema generation"""
    def greet(name: str) -> str:
        """Greet someone"""
        return f"Hello {name}"
    
    toolbox.register_tool(greet)
    schemas = toolbox.get_tool_schemas()
    
    assert len(schemas) == 1
    schema = schemas[0]["function"]
    assert schema["name"] == "greet"
    assert "parameters" in schema


def test_multiple_tools(toolbox):
    """Test multiple tool registration"""
    def tool1(): pass
    def tool2(): pass
    
    toolbox.register_tools([tool1, tool2])
    assert len(toolbox.get_tool_names()) == 2