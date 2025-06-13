PROVIDER_MAP = {
    "openai": {
        "model_env_key": "OPENAI_MODEL_NAME",
        "api_env_key": "OPENAI_API_KEY",
        "default_model": "gpt-4o-mini",
        "base_url_env_key": "OPENAI_BASE_URL",
    },
    "anthropic": {
        "model_env_key": "ANTHROPIC_MODEL_NAME",
        "api_env_key": "ANTHROPIC_API_KEY",
        "default_model": "claude-2",
        "base_url_env_key": "ANTHROPIC_BASE_URL",
    },
    "gemini": {
        "model_env_key": "GEMINI_MODEL_NAME",
        "api_env_key": "GEMINI_API_KEY",
        "default_model": "gemini-2.0-flash",
        "base_url_env_key": "GEMINI_BASE_URL",
    },
    "deepseek": {
        "model_env_key": "DEEPSEEK_MODEL_NAME",
        "api_env_key": "DEEPSEEK_API_KEY",
        "default_model": "deepseek-2.0",
        "base_url_env_key": "DEEPSEEK_BASE_URL",
    },
}

DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL = "gpt-4o-mini"  # Default model for OpenAI provider
