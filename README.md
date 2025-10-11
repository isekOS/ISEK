<!-- Banner Image -->
<p align="center">
  <img src="assets/banner.png" alt="ISEK Banner" width="100%" />
</p>

<h1 align="center">ISEK: Decentralized Agent-to-Agent (A2A) Network</h1>

<p align="center">
  <a href="https://pypi.org/project/isek/"><img src="https://img.shields.io/pypi/v/isek" alt="PyPI version" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT" /></a>
  <a href="mailto:team@isek.xyz"><img src="https://img.shields.io/badge/contact-team@isek.xyz-blue" alt="Email" /></a>
</p>

<h4 align="center">
    <a href="README.md">English</a> |
    <a href="README_CN.md">中文</a>
</h4>

---
**ISEK** is a decentralized agent network framework for building intelligent, collaborative agent-to-agent (A2A) systems. The Isek network integrates the Google **A2A** protocol and **ERC-8004** contracts to enable identity registration, reputation building, and cooperative task-solving. Together, these elements form a self-organizing, decentralized society of agents.
> 🧪 **ISEK is under active development.** Contributions, feedback, and experiments are highly welcome.

---

## What problem ISEK solve?

Our platform allows agent developers to run their agents locally. Through peer-to-peer connections, these agents join the ISEK network and can deliver services directly to users.
While most frameworks treat agents as isolated agent executors, **ISEK** focuses on the missing layer: **decentralized agent collaboration and coordination**. We believe the future of intelligent systems lies in **self-organizing agent networks** capable of context sharing, team formation, and collective reasoning — all without central control.
> ISEK is not just about running agents — it's about empowering them to **find each other, reason together, and act as a decentralized system.**

## Why ERC-8004 matters?

ERC-8004 provides a decentralized framework for identity, reputation, and validation registries, establishing the foundation for trustless verification and reputation management.
---

## 🌟 Features

- **🧠 Decentralized Cooperation
  Using the ERC-8004 trustless Agent Contract as our registry, we provide decentralized identity, reputation, and validation services. Agents can discover peers and collaborate directly — with no single point of failure.

- **🌐 Distributed Deployment
  Agent owners can run their agents 100% locally, mint an Agent NFT, and use an agent wallet to claim full ownership and control.

- **🔌 MCP-Based Agent Discovery
  Our map server connects to the agent discovery service, making it easy for users to find agents. Configure the MCP service once, and you can access agents directly through your favorite AI chatbot.

- **💻 Developer-Friendly CLI
  A streamlined CLI makes agent setup, deployment, and management fast and hassle-free.

---

## 🚀 Quick Start

```bash
python3 -m venv isek_env && source isek_env/bin/activate
```

### Installation
```bash
pip install isek
isek setup
```

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** (for P2P functionality)

> 💡 **Tip:** The `isek setup` command automatically handles both Python and JavaScript dependencies.


### Set Up Environment

Create a `.env` file:

```env
OPENAI_MODEL_NAME=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=your_api_key
```

### Wallet & Identity

ISEK now uses a simple local wallet manager and an ERC-8004 identity flow.

- Wallets are stored in `isek/web3/wallet.{NETWORK}.json` by default.
- ABI path is relative by default: `isek/web3/abi/IdentityRegistry.json`.
- Registration requires your agent card to provide a domain (we treat `url` as `domain`).

Add these keys to your `.env` (adjust for your network):

```env
# Network and chain
NETWORK=base-sepolia
ISEK_RPC_URL=https://sepolia.base.org
ISEK_CHAIN_ID=84532

# Identity contract
ISEK_IDENTITY_REGISTRY_ADDRESS=0xYourRegistryAddress
ISEK_IDENTITY_ABI_PATH=isek/web3/abi/IdentityRegistry.json

# Optional
ISEK_NETWORK_NAME=ISEK test network
ISEK_MAX_PRIORITY_FEE_GWEI=1
ISEK_EXPLORER_TX_URL_TEMPLATE=https://sepolia.basescan.org/tx/{tx_hash}
# Override wallet file location if needed
# ISEK_WALLET_DATA_FILE=isek/web3/wallet.base-sepolia.json
```

Register or resolve your agent identity:

```python
from isek.web3.isek_identiey import ensure_identity

# Any object with .name and .domain (or .url) works
agent_card = type("Card", (), {"name": "My Agent", "domain": "http://agent.isek.xyz"})()

address, agent_id, tx_hash = ensure_identity(agent_card)
print("wallet:", address, "agent_id:", agent_id, "tx:", tx_hash)
```

Notes:
- If the registry address or ABI are not set, the function returns your wallet address and skips on-chain registration.
- If the agent is already registered, it returns the existing `agent_id` without sending a transaction.


### Launch Agent

```python
from isek.agent.isek_agent import IsekAgent
from isek.models.openai import OpenAIModel
import dotenv
dotenv.load_dotenv()

agent = IsekAgent(
    name="My Agent",
    model=OpenAIModel(model_id="gpt-4o-mini"),
    description="A helpful assistant",
    instructions=["Be polite", "Provide accurate information"],
    success_criteria="User gets a helpful response"
)

response = agent.run("hello")
```

### Try Examples

In the examples folder, follow the examples from level 1 to level 10, and you should have a good understanding of ISEK

---

## 🧪 CLI Commands

```bash
isek setup       # Install Python and JavaScript dependencies
isek clean       # Clean temporary files
isek --help      # View available commands
```

---

## 🧱 Project Structure

```
isek/
├── examples                   # Sample scripts demonstrating Isek usage
├── isek                       # Core functionality and modules
│   ├── agent                  # Agent logic and behavior
│   ├── node                   # Node orchestration
│   ├── protocol               # Inter-Agent communication Protocol Layer
│   ├── memory                 # Agent state and context
│   ├── models                 # LLM backends and interfaces
│   ├── team                   # Multi-Agent Organization Interface
│   ├── tools                  # The toolkit library for Agents
│   ├── utils                  # Utility functions
│   ├── cli.py                 # CLI entry point
│   └── isek_center.py         # Local registry and coordinator
├── docs/                      # Documentation
└── README.md                  # Project overview and documentation
```
---

## 🌟 Star Us 😉

<img src="assets/star_gif.gif" alt="hippo" width="250"/>

---

## 🤝 Contributing

We welcome collaborators, researchers, and early adopters!

* 💬 Open issues or suggestions via [GitHub Issues](https://github.com/your-repo/issues)
* 📧 Contact us directly: [team@isek.xyz](mailto:team@isek.xyz)
* 📄 See our [Contribution Guidelines](CONTRIBUTING.md)

---

## 📜 License

Licensed under the [MIT License](LICENSE).

---
## ⚠️ Legal Notice

ISEK is an open-source, permissionless framework for building decentralized agent coordination systems.  
The contributors do not operate, control, or monitor any deployed agents or their behavior.  
By using this project, you accept full responsibility for your actions. See [LEGAL.md](./LEGAL.md) for more details.

---
<p align="center">
  Made with ❤️ by the <strong>Isek Team</strong><br />
  <em>Autonomy is not isolation. It's cooperation, at scale.</em>
</p>
