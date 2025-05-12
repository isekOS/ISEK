***************
Configuration
***************

Isek uses a YAML-based configuration system and a ``.env`` file to simplify setup and deployment. Through these configurations, you control core behaviors, models, networking, logging, agent-specific settings, and sensitive credentials like API keys.

Basic Structure
===============

An Isek configuration typically includes:

* **Agent settings** (``agent`` section)
* **Distributed mode settings** (``distributed`` section)
* **LLM and Embedding model configurations** (``llm`` and ``embedding`` sections)
* **Registry settings** for agent discovery (``registry`` section)
* **Environment variables** (in a ``.env`` file) for sensitive information

Example YAML
============

.. code-block:: yaml

   agent:
     debug_level: "DEBUG"  # Or "INFO", "WARNING", etc.
     persona_path: "path/to/your/persona.yml"

   distributed:
     enabled: true # Explicitly enable/disable distributed mode
     server: # Server settings for this node when in distributed mode
       host: "localhost"
       port: 8080

   llm:
     mode: "openai" # Specifies which LLM configuration to use
     openai: # Configuration specific to the 'openai' LLM mode
       # api_key can be set here directly (less secure) or via env var
       # api_key: "sk-your-actual-key-if-not-using-env"
       model_name: "gpt-4o"
       # Other OpenAI specific parameters like temperature, max_tokens, etc.

   embedding:
     mode: "openai" # Specifies which embedding configuration to use
     openai: # Configuration specific to the 'openai' embedding mode
       # api_key can be set here or via env var
       model_name: "text-embedding-3-small"
       # Optionally, specify 'dim' if the model supports it and you need a specific size
       # dim: 256

   registry:
     mode: "etcd" # or "isek_center"
     etcd: # Configuration for etcd if mode is "etcd"
       host: "127.0.0.1"
       port: 2379
       # Optional: parent_node_id: "my_app_nodes"
       # Optional: ttl: 60
     isek_center: # Configuration for isek_center if mode is "isek_center"
       host: "localhost"
       port: 8088

   # Note: For API keys like OPENAI_API_KEY, it's best practice to load them
   # from environment variables (e.g., from a .env file) within your Python
   # code (e.g., in IsekConfig or OpenAIModel) rather than direct interpolation
   # like "${OPENAI_API_KEY}" in YAML, as standard YAML loaders don't do this
   # by default. Your IsekConfig class would handle resolving these.

Example ``.env`` File
=====================

Store sensitive credentials safely in a ``.env`` file (this file is typically *not* committed to version control):

.. code-block:: bash

   # This file is usually loaded by a library like python-dotenv in your application
   OPENAI_API_KEY="your-actual-openai-api-key"
   OPENAI_BASE_URL="https://api.openai.com/v1" # Optional, if not using default
   OPENAI_MODEL_NAME="gpt-4o-mini" # Can be overridden by YAML

Agent Configuration
===================

The ``agent`` section defines basic behaviors:

* ``debug_level``: Sets the logging verbosity (e.g., "DEBUG", "INFO").
* ``persona_path``: Specifies the file path to load your agent's persona definition.

Distributed Mode
================

Configure network-enabled agents:

* ``distributed.enabled``: Set ``true`` for network-enabled agents; ``false`` for single, local agents.
* ``distributed.server``: If ``enabled`` is ``true``, this nested section defines the ``host`` and ``port`` your agent listens on for peer communication.

LLM and Embeddings
==================

Specify your language model (LLM) and embedding model:

* **LLM settings** (``llm`` section):
    * ``mode``: Specifies the LLM provider (e.g., "openai").
    * Provider-specific section (e.g., ``llm.openai``): Contains parameters like ``model_name``, and potentially ``api_key`` (though environment variables are preferred for keys).
* **Embedding settings** (``embedding`` section):
    * ``mode``: Specifies the embedding provider.
    * Provider-specific section (e.g., ``embedding.openai``): Contains parameters like ``model_name``.

Registry Configuration
======================

The registry is used by distributed agents for peer discovery:

* ``registry.mode``: Set to either ``"etcd"`` (for a production-grade distributed registry) or ``"isek_center"`` (for a simpler, built-in demo registry).
* ``registry.etcd`` or ``registry.isek_center``: Nested sections containing specific connection parameters for the chosen registry type.

Example Usage in Python
=======================

Load your configuration and initialize an agent:

.. code-block:: python

   from isek.isek_config import IsekConfig # Corrected import path based on previous files

   # Ensure your IsekConfig class handles loading .env variables if you use them
   # for API keys referenced in the YAML (e.g., via os.environ.get).
   config = IsekConfig("path/to/your/config.yml")
   agent = config.load_agent()

   agent.run("What is today's task?")


Best Practices
==============

* Always store sensitive information, such as API keys, in a secure ``.env`` file, and ensure this file is in your ``.gitignore``.
* Your application code (e.g., `IsekConfig` or model initializers) should be responsible for loading values from environment variables (e.g., using `os.environ.get("VARIABLE_NAME")`). Standard YAML loaders do not automatically interpolate `${VARIABLE_NAME}` syntax; this requires custom logic or a specialized YAML loader.
* Keep persona definitions and potentially large model configurations organized.
* Use the ``debug_level`` in the agent configuration for detailed logging during development.