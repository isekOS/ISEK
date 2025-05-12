.. isek documentation master file
   (Adapt as needed)

#####################################################################
Isek: Distributed Cooperative-Autonomous Multi-Agent Framework
#####################################################################

.. note::
   🧪 **Isek is under active development** — your feedback, experiments, and contributions are highly welcome.

**Isek** is a lightweight, modular, and distributed multi-agent framework built for the next generation of **cooperative autonomous systems**. Agents in Isek aren’t just isolated functions — they form a **decentralized society**, discovering peers, sharing context, and collaboratively solving complex tasks across nodes.

With built-in LLM integration and an intuitive CLI, Isek is ideal for researchers, developers, and builders designing intelligent, collaborative agents in distributed environments.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :hidden:

   installation
   quickstart
   user_guide/index
   api/index
   contributing


Key Features
================

*   **Cooperative Autonomy:** Agents autonomously discover suitable peers in the network, communicate, and collaborate to complete tasks in a decentralized fashion.
*   **Distributed Agent Orchestration:** Spin up and manage intelligent agents across multiple nodes with flexible task assignment and coordination.
*   **LLM Integration:** Built-in support for integrating Large Language Models such as OpenAI, enabling advanced NLP functionalities.
*   **Modular Design:** Highly modular architecture ensures ease of maintenance, scalability, and flexibility for customization.
*   **Lightweight and User-Friendly:** Designed for easy adoption, providing a streamlined user experience without complex setup or heavy dependencies.


Getting Started
===================

1.  **Installation:** Get Isek up and running quickly.
    See the :doc:`installation` guide for details (Python 3.8+ required).

    .. code-block:: bash

       pip install isek

2.  **Quick Start:** Dive into a basic example.
    Follow the :doc:`quickstart` guide to set up your environment and run a demo like `distributed_agent_demo`.


Command-Line Interface (CLI)
================================

Isek provides a simple CLI for common tasks:

.. code-block:: bash

   # Start the local registry/orchestrator
   isek registry

   # List and run examples
   isek example list
   isek example run <example_name>

   # Clean up temporary files
   isek clean

   # See all commands
   isek --help

For more details, explore the :doc:`user_guide/index`.


What’s Next? (Roadmap) 🌱
============================

We're actively working on enhancing Isek:

*   🔄 Real-time P2P agent messaging
*   🧭 Adaptive role assignment based on peer context
*   🌐 Decentralized discovery protocol
*   🧰 GUI Dashboard for agent orchestration

Stay tuned — and help shape the future of distributed autonomous systems!


Contributing 🤝
=================

We welcome collaborators, researchers, and early adopters.

*   Report issues or share ideas via `GitHub Issues <[Your GitHub Issues Link]>`_
*   Contact us: `team@isek.xyz <mailto:team@isek.xyz>`_
*   (Optional: Link to a dedicated contributing guide: :doc:`contributing`)


License
===========

This project is licensed under the `MIT License <[Link to your LICENSE file, e.g., https://github.com/your_org/isek/blob/main/LICENSE]>`_.


Indices and Tables
======================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. Footer (Optional)
.. Raw HTML can be used for more complex formatting if needed, but plain text is safer.

---

<p align="center">
Made with ❤️ by the <strong>Isek Team</strong><br>
<em>Autonomy is not isolation. It's cooperation, at scale.</em>
</p>