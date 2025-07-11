# 📈 Company Info Agent (Powered by LiteLLMModel and DeepSeek)

This example demonstrates how to build a company information agent using the [ISEK](https://github.com/isekOS/ISEK) framework. The agent integrates the `deepseek` large language model via  [`LiteLLMModel`](** https://github.com/isekOS/ISEK/tree/main/isek/models/litellm**)and can fetch stock codes and company information for companies.

---

## 🚀 Features

- Query company info by **company name**
- Retrieve **stock code** (e.g. `TSLA`)
- Fetch **basic stock info** and **company details** using tools
- Uses `DeepSeek-chat` LLM via [`LiteLLMModel`](** https://github.com/isekOS/ISEK/tree/main/isek/models/litellm**)
- Fully extensible with other models and tools via ISEK

---

## 🧠 How It Works

The agent uses the following components:

-  [`LiteLLMModel`](** https://github.com/isekOS/ISEK/tree/main/isek/models/litellm**): Wrapper for any OpenAI-compatible LLM (e.g., DeepSeek, GPT-4, Claude, etc.)
- [`base_info_tools`]: A collection of tools to retrieve stock codes, stock information, and company details.
- `IsekAgent`: Manages tool usage and reasoning based on instructions.

---

## 🧩 Set Up Environment

Before you try this example, don't forget to modify your .env file:

```bash
DEEPSEEK_API_KEY=your_deepseek_apikay
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

## 🔄 Other Example Configs

You can easily switch to other models and providers using [`LiteLLMModel`](** https://github.com/isekOS/ISEK/tree/main/isek/models/litellm**). Here are some common configurations:

#### ✅ DeepSeek via Ollama (local deployment)

```python
LiteLLMModel(
    provider="ollama",
    model_id="deepseek-chat",
    base_url="http://localhost:11434",
    api_env_key=None  # No API key needed for local use
)
```

#### ✅ Claude (Anthropic)

```python
LiteLLMModel(
    provider="anthropic",
    model_id="claude-3-opus-20240229",
    api_env_key="ANTHROPIC_API_KEY"
)
```