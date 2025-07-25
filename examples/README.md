# A collection of ISEK examples
Here we show you how to use isek to quickly build an agent, and how to build an Agent node and join the isek network

---

## 📦 Installation

```bash
  pip install isek
  isek setup
```

## 1️⃣ Set Up Environment

Create a `.env` file:

```env
OPENAI_MODEL_NAME=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=your_api_key
```

## 🧪 Understanding how ISEK works

- 【LV1】Show you how to build a simple agent
  - [lv1_single_agent.py](lv1_single_agent.py) 
- 【LV2】Show you how to load tools for the agent and support MCP
  - [lv2_tool_agent.py](lv2_tool_agent.py) 
  - [lv2_fastmcp_tool_agent.py](lv2_fastmcp_tool_agent.py)
- 【LV3】Show you the agent's memory and manages contextual information through sessions
  - [lv3_memory_agent.py](lv3_memory_agent.py)
- 【LV4】Create an advanced agent with memory management and tools
  - [lv4_memory_tool_agent.py](lv4_memory_tool_agent.py)
- 【LV5】Create a multi-agent system and complete tasks
  - [lv5_team_agent.py](lv5_team_agent.py)
- 【LV6】Create a multi-agent system and complete tasks
  - [lv6_team_agent_plus.py](lv6_team_agent_plus.py)
- 【LV7】Deploy isek nodes locally and implement node interaction
  - [lv7_node_local.py](lv7_node_local.py)
- 【LV8】Load the agent for the node and test the remote communication capability
  - [lv8_node_v2_server.py](lv8_node_v2_server.py)
  - [lv8_node_v2_client.py](lv8_node_v2_client.py)
- 【LV9】Load the agent for the node and complete the task through remote communication
  - [lv9_agent_on_node_server.py](lv9_agent_on_node_server.py)
  - [lv9_agent_on_node_client.py](lv9_agent_on_node_client.py)
- 【LV10】Show you how to enable nodes to have p2p communication capabilities and achieve NAT penetration
  - [lv10_agent_p2p_node_server.py](lv10_agent_p2p_node_server.py)
  - [lv10_agent_p2p_node_client.py](lv10_agent_p2p_node_client.py)

    