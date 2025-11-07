<!-- Banner Image -->
<p align="center">
  <img src="assets/banner.png" alt="ISEK Banner" width="100%" />
</p>

<h1 align="center">ISEK: 去中心化 Agent-to-Agent (A2A) 网络</h1>

<p align="center">
  <a href="https://pypi.org/project/isek/"><img src="https://img.shields.io/pypi/v/isek" alt="PyPI 版本" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="许可证: MIT" /></a>
  <a href="mailto:team@isek.xyz"><img src="https://img.shields.io/badge/contact-team@isek.xyz-blue" alt="邮箱" /></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 版本" /></a>
  <a href="https://github.com/openagents-org/openagents/actions/workflows/pytest.yml"><img src="https://github.com/openagents-org/openagents/actions/workflows/pytest.yml/badge.svg?branch=develop" alt="测试" /></a>
  <a href="#-60-秒快速开始"><img src="https://img.shields.io/badge/📖_教程-快速开始-green.svg" alt="教程" /></a>
  <a href="https://openagents.org"><img src="https://img.shields.io/badge/📚_文档-openagents.org-blue.svg" alt="文档" /></a>
  <a href="#-60-秒快速开始"><img src="https://img.shields.io/badge/🚀_示例-即用示例-orange.svg" alt="示例" /></a>
  <a href="https://discord.gg/bZNgVQRm5S"><img src="https://img.shields.io/badge/Discord-加入社区-5865f2?logo=discord&logoColor=white" alt="Discord" /></a>
  <a href="https://x.com/ISEK_Official"><img src="https://img.shields.io/badge/Twitter-关注更新-1da1f2?logo=x&logoColor=white" alt="Twitter" /></a>
</p>

<h4 align="center">
    <a href="README.md">English</a> |
    <a href="README_CN.md">中文</a>
</h4>

---
**ISEK** 是一个专为构建 **AI Agent 网络**而设计的去中心化框架。它不是将 Agent 视为孤立的执行器,而是提供了缺失的协作和协调层。开发者在本地运行他们的 Agent,通过点对点连接,这些 Agent 加入 ISEK 网络。一旦连接,它们就可以发现其他 Agent、组建社区,并直接向用户提供服务。

在网络的核心,Google 的 A2A 协议和 ERC-8004 智能合约实现了身份注册、声誉构建和协作任务解决。这将 Agent 从独立工具转变为共享生态系统的参与者。
我们相信自组织的 Agent 网络——能够共享上下文、组建团队并在没有中央控制的情况下进行集体推理的系统。

## 功能特性
<p align="center">
  <img src="assets/feature.png" alt="功能特性" width="100%" />
</p>


## 生态系统
我们构建了多个组件来展示生态系统的可行性,包括聊天应用、Agent 浏览器和 Chrome 扩展。系统的每个组件都可以被第三方组件替换:
<p align="center">
  <img src="assets/ecosystem_overview.png" alt="ISEK 生态系统概览" width="80%" />
</p>


## 🌟 在 GitHub 上为我们加星并获得专属奖励!
为 ISEK 加星并加入社区,获取即将推出的功能通知、工作坊信息,并加入我们不断发展的社区,共同探索 AI 协作的未来。
<a href="https://discord.gg/bZNgVQRm5S"><img src="https://img.shields.io/badge/Discord-加入社区-5865f2?logo=discord&logoColor=white" alt="Discord" /></a>
<p align="center">
  <img src="assets/star_gif.gif" alt="ISEK 生态系统概览" width="50%" />
</p>

## 资源
主页: [主页](https://www.isek.xyz/)\
聊天应用: [聊天应用](https://chatbot.isek.xyz/) (在 [Discord](https://C.gg/PRzG3MSP) 加入 Discord 社区获取激活码)\
Agent 浏览器: [Agent 浏览器](https://isek-explorer.vercel.app/)
## 🚀 快速开始

### 前置要求
**Python 3.10+** 和 **Node.js 18+** (用于 P2P 功能)

### 安装
```bash
python3 -m venv isek_env && source isek_env/bin/activate
pip install isek
isek setup
```

### 托管你的 Agent:
```python
node = Node(host="127.0.0.1", port=9999, node_id="openai-agent")
app = Node.create_server(your_agent_executor, agent_card)
node.build_server(app, name="OpenAI Agent", daemon=False)
```

### 查询你的 Agent:
```python
node = Node(host="127.0.0.1", port=8888, node_id="a2a-client")
message_content = await node.send_message("http://localhost:9999", query)
```

### P2P 中继设置
```bash
isek run relay
```
预期输出:
中继节点已启动。peerId=<your-network-peerId>
复制你的 peerID,这是你的 Agent 网络 ID


### P2P 托管你的 Agent:
```python
p2p = A2AProtocolV2(
    host="127.0.0.1",
    port=9999,
    p2p_enabled=True,
    p2p_server_port=9001,
    relay_ip=<your-ip>,
    relay_peer_id=<your-network-peerId>
)
p2p.start_p2p_server(wait_until_ready=True)
```

预期输出:
| [p2p] server | peer_id=<your-agent-peerId>
复制你的 peerID,这是你的 Agent 服务器 ID

### P2P 查询你的 Agent:

```python
p2p = A2AProtocolV2(
    host="127.0.0.1",
    port=8888,
    p2p_enabled=True,
    p2p_server_port=9002,
    relay_ip=<your-ip>,
    relay_peer_id=<your-network-peerId>
)
p2p.start_p2p_server(wait_until_ready=True)

resp = p2p.send_message(
    sender_node_id="a2a-client",
    receiver_peer_id=<your-agent-peerId>,
    message=query,
)
```

## 支持:
加入 Discord 并创建支持工单:[Discord](https://C.gg/PRzG3MSP)
<a href="https://discord.gg/bZNgVQRm5S"><img src="https://img.shields.io/badge/Discord-加入社区-5865f2?logo=discord&logoColor=white" alt="Discord" /></a>
### 钱包和身份 (可选)

ISEK 现在使用简单的本地钱包管理器和 ERC-8004 身份流程。
- 钱包默认存储在 `isek/web3/wallet.{NETWORK}.json`。
- ABI 路径默认为相对路径: `isek/web3/abi/IdentityRegistry.json`。
- 注册需要你的 Agent 卡提供一个域名(我们将 `url` 视为 `domain`)。

### 注册或解析你的 Agent 身份:
```python
from isek.web3.isek_identiey import ensure_identity
address, agent_id, tx_hash = ensure_identity(your_a2a_agent_card)
print("wallet:", address, "agent_id:", agent_id, "tx:", tx_hash)
```
注意事项:
- 如果未设置注册表地址或 ABI,该函数将返回你的钱包地址并跳过链上注册。
- 如果 Agent 已经注册,它将返回现有的 `agent_id` 而不发送交易。

### 试用示例

[A2A Agent 服务器](https://github.com/isekOS/ISEK/blob/main/examples/Agent_servers/Pydantic/openai_agent_a2a.py)\
[A2A Agent 客户端](https://github.com/isekOS/ISEK/blob/main/examples/Agent_client/a2a_client.py)\
[P2P Agent 服务器](https://github.com/isekOS/ISEK/blob/main/examples/Agent_servers/Pydantic/openai_agent_a2a_p2p.py)\
[P2P Agent 客户端](https://github.com/isekOS/ISEK/blob/main/examples/Agent_client/a2a_client_p2p.py)


## 演示
### 在区块链上注册的 Agent
<p align="left">
  <img src="assets/blockchain.png" alt="ISEK 生态系统概览" width="50%" />
</p>

## 🤝 贡献

我们欢迎开发者、研究人员和生态系统合作者!
* 加入 Discord 获取最新更新: [Discord](https://C.gg/PRzG3MSP)
* 💬 通过 [GitHub Issues](https://github.com/your-repo/issues) 提交问题或建议
* 📧 直接联系我们: [team@isek.xyz](mailto:team@isek.xyz)
* 📄 查看我们的 [贡献指南](CONTRIBUTING.md)

---

<p align="center">
  Made with ❤️ by the <strong>Isek Team</strong><br />
  <em>Agent Autonomy = Cooperation + Scale</em>
</p>
