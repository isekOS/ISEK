from abc import ABC, abstractmethod
from isek.models.openai.chat import OpenAIModel

# from isek.embedding.openai_embedding import OpenAIEmbedding
from isek.models.abstract_model import AbstractModel

# from isek.embedding.abstract_embedding import AbstractEmbedding
from typing import Optional, List, Callable
from isek.agent.persona import Persona
from isek.agent.memory import AgentMemory
from isek.agent.toolbox import ToolBox
import time

# add logging
from isek.util.logger import logger


class AbstractAgent(ABC):
    """
    An abstract base class for creating intelligent agents.

    This class provides a foundational structure for agents, including
    persona management, interaction with language models, memory,
    and tool usage.
    """

    def __init__(
        self,
        persona: Persona = None,
        model: Optional[AbstractModel] = None,
        tools: List[Callable] = None,
        deepthink_enabled: bool = False,
        **kwargs,
    ) -> None:
        """
        Initializes the AbstractAgent.

        :param persona: The persona defining the agent's characteristics and behavior.
                        Defaults to :class:`isek.agent.persona.Persona.default()` if None.
        :type persona: typing.Optional[isek.agent.persona.Persona]
        :param model: The language model to be used by the agent.
                      Defaults to :class:`isek.llm.openai_model.OpenAIModel()` if None.
        :type model: typing.Optional[isek.llm.abstract_model.AbstractModel]
        :param tools: A list of callable tools that the agent can use. Defaults to None.
        :type tools: typing.Optional[typing.List[typing.Callable]]
        :param deepthink_enabled: A flag to enable or disable the deep thinking capability.
                                  Defaults to False.
        :type deepthink_enabled: bool
        :param kwargs: Additional keyword arguments for future compatibility or extensions.
        """
        self.persona = persona or Persona.default()
        self.model = model or OpenAIModel()
        self.memory_manager = AgentMemory()
        self.tool_manager = ToolBox(persona=self.persona)
        self.deepthink_enabled = deepthink_enabled
        # Register action tools
        if tools:
            self.tool_manager.register_tools(tools)

    @abstractmethod
    def build(self, daemon=False):
        """
        Abstract method to build or set up the agent.

        This method should be implemented by subclasses to perform any
        necessary initialization or setup before the agent starts running.

        :param daemon: If True, the agent might be set up to run as a daemon process.
                       Defaults to False.
        :type daemon: bool
        """
        pass

    def run(self, input: str = None) -> None:
        """
        Runs a single cycle of the agent's operation.

        The agent processes the input, generates a response, and logs the interaction.

        .. note::
            The type hint for the return value is ``None``, but the implementation
            returns a string response. The docstring reflects the implementation.
            Consider updating the type hint to ``-> str`` for consistency.

        :param input: User instructions or environment signals, such as text.
                      Defaults to None.
        :type input: typing.Optional[str]
        :return: The agent's response to the input.
        :rtype: str
        """
        logger.info(f"[{self.persona.name}] ++++++++++Cycle Started++++++++++")
        response = self.response(input)
        logger.info(f"[{self.persona.name}][Response]: {response}")
        logger.info(f"[{self.persona.name}] ----------Cycle Ended------------")

        return response

    def heartbeat(self):
        """
        Executes a heartbeat cycle for the agent.

        This function is intended to be called periodically to keep the agent
        active or to perform routine tasks when no explicit input is given.
        It calls the :meth:`run` method with no input.
        """
        self.run()

    def run_cli(self):
        """
        Runs the agent in a command-line interface (CLI) mode.

        This method continuously prompts the user for input and processes it
        using the :meth:`run` method until the user types "exit".
        """
        while True:
            time.sleep(0.2)
            text = input("Enter your command: ")
            if text == "exit":
                break
            self.run(text)

    def response(self, input: str) -> str:
        """
        Generates a response to the given input.

        This method orchestrates the agent's core logic:

        1. Logs the trigger (input or heartbeat).
        2. Stores the user input in memory (if provided).
        3. Builds prompt templates incorporating persona, system instructions, tools, and conversation history.
        4. Optionally performs a "deep think" step to decompose the task.
        5. Enters a loop to interact with the language model:
           a. Sends the current messages and available tools to the model.
           b. Appends the model's response to the message history.
           c. If the response contains content, stores it in memory.
           d. If there are no tool calls, returns the content.
           e. If there are tool calls, executes each tool, appends the result to messages, and continues the loop.

        :param input: User instructions or environment signals, such as text.
                      The method internally handles cases where `input` might be None or empty,
                      though its type hint is `str`.
        :type input: str
        :return: The agent's textual response to the input.
        :rtype: str
        """
        if input is not None and input != "":
            logger.info(f"[{self.persona.name}][Trigger: Input]: {input}")
            self.memory_manager.store_memory_item("User:" + input)
        else:
            logger.info(f"[{self.persona.name}][Trigger: Heartbeat]")

        # Build template for action phase
        template = self._build_templates()
        # logger.info(f"[{template}] ")

        messages = [{"role": "user", "content": template}]

        # Setup available tools for action phase
        # tools = self.tool_manager.get_tool_names()
        tool_schemas = self.tool_manager.get_tool_schemas()

        if self.deepthink_enabled:
            # Decompose the task into subtasks
            deepthink = (
                self.model.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "you are a deep thnker and you are going to think deeply about the user's task and return yout thinking step as text, limit your think to 50 words",
                        }
                    ]
                    + messages,
                    systems=[],
                    tool_schemas=tool_schemas or None,
                )
                .choices[0]
                .message
            )
            # print(deepthink)
            messages.append(deepthink)

        # Main action loop
        while True:
            # Get AI completion with tool calling
            response = (
                self.model.create(
                    messages=[
                        {"role": "system", "content": "you are a helpful assistant"}
                    ]
                    + messages,
                    systems=[],
                    tool_schemas=tool_schemas or None,
                )
                .choices[0]
                .message
            )
            messages.append(response)

            # Process text response
            if response.content:
                self.memory_manager.store_memory_item("Agent:" + response.content)

            # Check if we're done with tool calls
            if not response.tool_calls:
                return response.content

            # Handle tool calls
            for tool_call in response.tool_calls:
                result = self.tool_manager.execute_tool_call(tool_call=tool_call)
                result_message = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
                messages.append(result_message)

    def _build_templates(self) -> str:
        """
        Builds the prompt templates for the agent's interaction with the LLM.

        This method aggregates various pieces of information, such as persona details
        (name, bio, lore, knowledge), system instructions, routine tasks (if any),
        available tools, and recent conversation history, into a structured prompt string.

        :return: A string containing the compiled prompt templates.
        :rtype: str
        """
        # Get recent memory items
        recent_memory = self.memory_manager.get_recent_memory_items()
        # state = self.memory_manager.get_all_state_variables()
        # tasks = self.memory_manager.get_pending_tasks()

        # Return all templates as a dictionary
        routine = ""
        if "routine" in self.persona.__dict__:
            routine = self.persona.routine

        templates = {
            "persona": f"""       
                "You Name is:
                "{self.persona.name}"
                "You are a {self.persona.bio}"
                "Your mission is to {self.persona.lore}"
                "You have the following knowledge: {self.persona.knowledge}"
            """,
            "system": """
                "You have the freedom to reason and act to help you achieve your goal."
                "try your best to use tools to improve responses quality."
                "please be concise and clear in your responses."
                "in most cases, you should only provide one or two sentence."
                "in rare cases, you may provide a longer response." 
            """,
            "routine": f"""
            "{routine}"
            """,
            "tool": f"""
                "You have the following tools available: {self.tool_manager.get_tool_names()}"
            """,
            "closing": f"""
                response base on the following conversation: 
                {recent_memory}
            """,
        }
        # add all the templates together
        template = ""
        for key in templates:
            template += templates[key]
        return template

    def decompose_task(self, command: str) -> str:
        """
        Decomposes a given command or task into a list of subtasks using the LLM.

        This method prompts the language model to break down a complex task
        into a list of high-level subtasks. The subtasks are expected to be
        returned by the model as a Python list string.

        :param command: The command or task to be decomposed.
        :type command: str
        :return: A string representation of a list of subtasks
                 (e.g., '["Subtask 1", "Subtask 2"]').
        :rtype: str
        """
        task_decomposer_template = f"""
        As a Task Decomposer, your objective is to divide the given task into high level subtasks.
        You have been provided with the following objective:
        {command}

        Please format the subtasks as a python list with 3 or less tasks, each tasks contains less than 10 words, as demonstrated below, output nothing else:
        ["Subtask 1", "Subtask 2", "Subtask 3"]
        
        Each subtask should be concise, concrete, and achievable.
        Ensure that the task plan is created without asking any questions.
        Be specific and clear.
        """
        response = (
            self.model.create(
                messages=[{"role": "system", "content": task_decomposer_template}],
                systems=[],
                tool_schemas=None,
            )
            .choices[0]
            .message
        )

        # parse the response to get the subtasks
        subtasks_str = response.content
        try:
            subtasks = eval(subtasks_str)  # Potential security risk with eval
            if not isinstance(subtasks, list):
                logger.warning(
                    f"[{self.persona.name}] Subtask decomposition did not return a list: {subtasks_str}"
                )
                return str([])  # Return empty list string on failure
        except Exception as e:
            logger.error(
                f"[{self.persona.name}] Error parsing subtasks: {e}. Response was: {subtasks_str}"
            )
            return str([])  # Return empty list string on error

        # for subtask in subtasks:
        #   self.memory_manager.create_task(subtask)
        logger.info(f"[{self.persona.name}] Subtasks: {subtasks}")
        return str(subtasks)
