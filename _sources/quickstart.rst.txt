================
Quick Start
================

This guide will walk you through the basic steps to install ISEK, set up your environment, and launch your first decentralized agent.

Prerequisites
-------------

*   **Python 3.8 or higher**
*   An **OpenAI API Key** (or access to a compatible LLM API)

Installation
------------

Install ISEK using pip:

.. code-block:: bash

   pip install isek

Setting Up Your Environment
---------------------------

ISEK requires certain environment variables to be set, particularly for LLM integration.

1.  **Create a ``.env`` file**:
    In your project's root directory (or where you plan to run your agent scripts), create a file named ``.env``.

2.  **Add API Configuration**:
    Populate the ``.env`` file with your LLM API details. For OpenAI, it would look like this:

    .. code-block:: bash

       OPENAI_MODEL_NAME=gpt-4o-mini
       OPENAI_BASE_URL=https://api.openai.com/v1
       OPENAI_API_KEY=your_api_key

    .. note::
       Replace ``your_api_key`` with your actual OpenAI API key. Adjust ``OPENAI_MODEL_NAME`` and ``OPENAI_BASE_URL`` if you are using a different model or a custom/proxy endpoint.

Running Your First Agent
------------------------

Follow these steps to launch the ISEK registry and your first agent.

1.  **Start the ISEK Registry**:
    The registry is a local component that helps agents discover each other. Open a terminal window and run:

    .. code-block:: bash

       isek registry

    Keep this terminal window open. The registry needs to be running for agents to connect.

2.  **Launch an Agent**:
    In a *new* terminal window (while the registry is still running in the other), create a Python script (e.g., ``run_my_agent.py``) with the following content:

    .. code-block:: python

       from dotenv import load_dotenv
       from isek.agent.distributed_agent import DistributedAgent

       # Load environment variables from .env file
       load_dotenv()

       print("Initializing agent...")
       agent = DistributedAgent()

       print("Building agent (daemon=True)...")
       # daemon=True runs the agent's internal services (like its API server)
       # in background threads, allowing the CLI to be interactive.
       agent.build(daemon=True)

       print("Running agent CLI. Type 'help' for commands or 'exit' to quit.")
       agent.run_cli()

       print("Agent CLI exited.")

    Save the file and then run it:

    .. code-block:: bash

       python run_my_agent.py

    You should now be able to interact with your decentralized agent directly through the command-line interface that appears in your terminal. Try typing ``help`` to see available agent commands.

Exploring Further
-----------------

Congratulations! You've successfully set up and launched your first ISEK agent.

*   **Interact with your agent**: Use the CLI that appeared after running your Python script.
*   **ISEK CLI Utilities**: Use the main ``isek`` command for other operations:
    .. code-block:: bash

       isek --help      # View available commands
       isek clean       # Clean temporary files

*   **Examples**: Check out the ``examples/`` directory in the ISEK project repository for more advanced use cases and demonstration scripts.

For more detailed information on configuration, features, and contributing, please refer to the main project documentation.