************
Agents
************

In Isek, an **Agent** is an intelligent entity that autonomously acts, communicates, collaborates, and learns within a decentralized network. Each agent combines reasoning, tool usage, memory, and distinct personas to perform tasks and achieve goals.

Agent Architecture
==================

An Isek Agent is structured into two key components:

* **Agent Core**: Responsible for internal reasoning, decision-making, task execution, and memory management.
* **Communication Node**: Manages networking aspects such as registration, peer discovery, and message exchange.

This modular approach ensures flexible deployment—agents think locally but coordinate globally.

Using Personas
==============

A persona defines an agent's identity, guiding its interactions, responses, and overall behavior.

Personas include:

* **Name & Role**: Agent's identity.
* **Mission (Lore)**: Long-term objectives guiding agent behavior.
* **Domain Knowledge**: Areas of expertise (e.g., AI, finance).
* **Routine** *(optional)*: Regular behaviors or initial planning actions.

Example:

.. code-block:: python

   from isek.agent.persona import Persona
   from isek.agent.single_agent import SingleAgent # Assuming SingleAgent is needed here

   researcher = Persona(
       name="Athena",
       bio="AI research assistant",
       lore="advance AI research knowledge",
       knowledge="machine learning, NLP, research trends",
       routine="identify new trends daily"
   )

   agent = SingleAgent(persona=researcher)

Core Capabilities
=================

Agents have powerful built-in features:

* **Tool Use**: Agents dynamically invoke APIs, scripts, or other tools to achieve their goals.
* **Task Decomposition**: Complex tasks are broken into smaller, manageable subtasks.
* **Memory**: Agents remember interactions, outcomes, and maintain internal states, improving over time.
* **Partner Discovery**: Find capable peers across the network dynamically.
* **Peer Communication**: Exchange messages with peers to coordinate actions and collaborate.

Example Task Decomposition:

.. code-block:: python

   # Assuming 'agent' is an initialized agent instance
   subtasks = agent.decompose_task("Organize a virtual AI conference")
   # subtasks → ["Identify keynote speakers", "Schedule sessions", "Invite participants"]

Running an Agent
================

Agents can run interactively via command-line:

.. code-block:: python

   # Assuming 'agent' is an initialized agent instance
   agent.run_cli()

Or respond to single queries:

.. code-block:: python

   # Assuming 'agent' is an initialized agent instance
   response = agent.run("What's the latest breakthrough in AI?")
   print(response)

Heartbeat and Autonomy
======================

Agents support autonomous background tasks using a heartbeat:

.. code-block:: python

   # Assuming 'agent' is an initialized agent instance
   agent.heartbeat()

This periodically triggers internal routines, updates, or peer interactions without direct user input.

Deep Thinking Mode
==================

Enabling `deepthink_enabled` allows agents to reflect more deeply before responding, leading to smarter, more structured outcomes:

.. code-block:: python

   from isek.agent.single_agent import SingleAgent # Assuming SingleAgent
   # Assuming 'researcher' persona is defined as above

   agent = SingleAgent(persona=researcher, deepthink_enabled=True)

Decentralized Cooperation
=========================

Agents naturally form decentralized, evolving societies. Without any central control, agents autonomously:

* Form coalitions on-demand
* Delegate tasks dynamically
* Solve complex tasks collectively

Example Distributed Agent:

.. code-block:: python

   from isek.agent.distributed_agent import DistributedAgent
   # Assuming 'researcher' persona is defined as above

   dist_agent = DistributedAgent(persona=researcher)
   dist_agent.run("Collaborate with peers to summarize recent AI developments")

Tips for Effective Use
======================

* Clearly define your agent's persona and mission.
* Leverage memory to improve agent learning and context awareness.
* Use tools extensively—agents perform best when empowered to act.
* Enable deep thinking for strategic tasks that require careful planning.