"""encoding=utf-8"""

import time
import os
import json
from isek.util.logger import logger  # Assuming logger is configured
from isek.models.abstract_model import AbstractModel
from isek.util.tools import (
    load_json_from_chat_response,
)  # Assuming these utilities exist
from typing import List, Optional, Dict, Callable, Any  # Added Any
from openai import OpenAI
from openai.types.chat import (
    ChatCompletion,
)  # For type hinting the response of `create`

# Define a type alias for message dictionaries for clarity
ChatMessage = Dict[str, str]  # e.g., {"role": "user", "content": "Hello"}
ToolSchema = Dict[str, Any]  # e.g., the schema for a tool/function


class OpenAIModel(AbstractModel):
    """
    An implementation of :class:`~isek.llm.abstract_model.AbstractModel`
    that uses OpenAI's API for chat completions.

    This class provides methods to interact with OpenAI's chat models (like GPT-3.5, GPT-4)
    to generate text, JSON objects, and handle tool/function calling.
    It handles API key and endpoint configuration, request formatting, and retries.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initializes the OpenAIModel client.

        Configuration (model name, API key, base URL) is sourced from parameters,
        falling back to environment variables (`OPENAI_MODEL_NAME`, `OPENAI_API_KEY`,
        `OPENAI_BASE_URL`) if parameters are not provided.

        :param model_name: The name of the OpenAI chat model to use (e.g., "gpt-3.5-turbo", "gpt-4").
                           If `None`, defaults to the value of `OPENAI_MODEL_NAME` environment variable,
                           or remains `None` if the environment variable is also not set (which might lead
                           to errors if not specified before making API calls).
        :type model_name: typing.Optional[str]
        :param api_key: The OpenAI API key. If `None`, defaults to `OPENAI_API_KEY` environment variable.
        :type api_key: typing.Optional[str]
        :param base_url: The base URL for the OpenAI API. Useful for proxying or using compatible
                         non-OpenAI endpoints. If `None`, defaults to `OPENAI_BASE_URL` environment variable,
                         or the default OpenAI API URL if the environment variable is also not set.
        :type base_url: typing.Optional[str]
        """
        super().__init__()
        self.model_name: Optional[str] = model_name or os.environ.get(
            "OPENAI_MODEL_NAME"
        )
        # Ensure model_name is set, otherwise API calls will fail.
        if not self.model_name:
            logger.warning(
                "OpenAIModel initialized without a model_name. API calls may fail. "
                "Set it via parameter or OPENAI_MODEL_NAME environment variable."
            )
            # Consider raising an error here if a model_name is strictly required at init.
            # For now, allowing it to be None and potentially fail later.

        _base_url: Optional[str] = base_url or os.environ.get("OPENAI_BASE_URL")
        _api_key: Optional[str] = api_key or os.environ.get("OPENAI_API_KEY")

        self.client: OpenAI = OpenAI(base_url=_base_url, api_key=_api_key)
        logger.info(
            f"OpenAIModel initialized with model: {self.model_name}, base_url: {_base_url if _base_url else 'default'}"
        )

    def generate_json(
        self,
        prompt: str,
        system_messages: Optional[List[ChatMessage]] = None,
        retry: int = 3,
        check_json_def: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        """
        Generates a JSON object from the model based on a prompt.

        It attempts to parse the model's response content as JSON.
        Includes retry logic and an optional validation function for the parsed JSON.

        .. note::
            To reliably get JSON output, ensure your prompt explicitly instructs
            the model to generate JSON. Newer OpenAI models support a `response_format`
            parameter (e.g., `{"type": "json_object"}`) in the `create` method,
            which could be integrated here for more robust JSON generation.

        :param prompt: The user prompt instructing the model to generate JSON.
        :type prompt: str
        :param system_messages: An optional list of system messages to prepend to the conversation.
        :type system_messages: typing.Optional[typing.List[ChatMessage]]
        :param retry: The number of times to retry the API call if it fails or JSON parsing fails.
                      Defaults to 3.
        :type retry: int
        :param check_json_def: An optional callable that takes the parsed JSON dictionary
                               as input and should raise an exception if the JSON is invalid.
                               If `None`, no custom validation is performed beyond basic parsing.
        :type check_json_def: typing.Optional[typing.Callable[[typing.Dict[str, typing.Any]], None]]
        :return: A dictionary parsed from the model's JSON response.
        :rtype: typing.Dict[str, typing.Any]
        :raises RuntimeError: If the API call or JSON processing fails after all retries.
        :raises ValueError: If JSON parsing fails and `load_json_from_chat_response` also fails.
        :raises Exception: If `check_json_def` raises an exception.
        """
        if not self.model_name:
            raise ValueError(
                "OpenAIModel model_name is not set. Cannot make API calls."
            )

        for i in range(retry):
            try:
                # For robust JSON, consider adding response_format={"type": "json_object"}
                # to the `create` call if the model supports it.
                # This would require modifying the `create` method or passing it as a kwarg.
                response: ChatCompletion = self.create(
                    messages=[{"role": "user", "content": prompt}],
                    systems=system_messages,
                    # Example for future: response_format={"type": "json_object"}
                )
                response_content = response.choices[0].message.content
                if response_content is None:
                    raise ValueError("Model response content is None.")

                json_result: Dict[str, Any]
                try:
                    json_result = json.loads(response_content)
                except json.JSONDecodeError:
                    # Fallback to a custom JSON extraction logic if direct parsing fails
                    json_result = load_json_from_chat_response(
                        response_content
                    )  # This must return a dict or raise

                if check_json_def:
                    check_json_def(
                        json_result
                    )  # This function should raise if validation fails

                return json_result
            except Exception as e:
                logger.warning(
                    f"Model [{self.model_name}] generate_json attempt {i+1}/{retry} failed: {e}"
                )
                if i == retry - 1:  # Last attempt
                    logger.error(
                        f"generate_json failed after {retry} retries for model [{self.model_name}]."
                    )
                    raise RuntimeError(
                        f"Failed to generate valid JSON after {retry} retries."
                    ) from e
                time.sleep(1 * (i + 1))  # Exponential backoff basic
        # Should not be reached if retry > 0
        raise RuntimeError(
            "generate_json failed after all retries (unexpectedly reached end of loop)."
        )

    def generate_text(
        self,
        prompt: str,
        system_messages: Optional[List[ChatMessage]] = None,
        retry: int = 3,
    ) -> str:
        """
        Generates plain text from the model based on a prompt.

        Includes retry logic for API calls.

        :param prompt: The user prompt for text generation.
        :type prompt: str
        :param system_messages: An optional list of system messages to prepend.
        :type system_messages: typing.Optional[typing.List[ChatMessage]]
        :param retry: The number of times to retry the API call if it fails. Defaults to 3.
        :type retry: int
        :return: The text content generated by the model.
        :rtype: str
        :raises RuntimeError: If the API call fails after all retries.
        """
        if not self.model_name:
            raise ValueError(
                "OpenAIModel model_name is not set. Cannot make API calls."
            )

        for i in range(retry):
            try:
                response: ChatCompletion = self.create(
                    messages=[{"role": "user", "content": prompt}],
                    systems=system_messages,
                )
                response_content = response.choices[0].message.content
                if response_content is None:
                    # This might happen if the model's generation is stopped early or filters trigger.
                    logger.warning(
                        f"Model [{self.model_name}] generate_text attempt {i+1}/{retry} returned None content."
                    )
                    # Depending on requirements, either treat as error or return empty string.
                    # For now, let's try again. If consistently None, the loop will exhaust.
                    if i == retry - 1:
                        raise ValueError("Model consistently returned None content.")
                    raise InterruptedError(
                        "Model returned None content, retrying."
                    )  # Custom signal to retry
                return response_content
            except (
                InterruptedError
            ):  # Catch the signal to retry specifically for None content
                if i < retry - 1:
                    time.sleep(1 * (i + 1))
                    continue
                # If it's the last retry and still None, it will fall through to the general exception.
            except Exception as e:
                logger.warning(
                    f"Model [{self.model_name}] generate_text attempt {i+1}/{retry} failed: {e}"
                )
                if i == retry - 1:  # Last attempt
                    logger.error(
                        f"generate_text failed after {retry} retries for model [{self.model_name}]."
                    )
                    raise RuntimeError(
                        f"Failed to generate text after {retry} retries."
                    ) from e
                time.sleep(1 * (i + 1))  # Exponential backoff basic
        # Should not be reached if retry > 0
        raise RuntimeError(
            "generate_text failed after all retries (unexpectedly reached end of loop)."
        )

    def create(
        self,
        messages: List[ChatMessage],
        systems: Optional[List[ChatMessage]] = None,
        tool_schemas: Optional[List[ToolSchema]] = None,
        **kwargs: Any,  # Allow passing other ChatCompletion.create parameters
    ) -> ChatCompletion:
        """
        Creates a chat completion using the OpenAI API.

        This is the core method for interacting with the chat model. It can handle
        system messages, user/assistant messages, and tool/function schemas.

        :param messages: A list of message objects, where each object has a "role"
                         (e.g., "user", "assistant", "tool") and "content".
        :type messages: typing.List[ChatMessage]
        :param systems: An optional list of system message objects. These are typically
                        prepended to the `messages` list.
        :type systems: typing.Optional[typing.List[ChatMessage]]
        :param tool_schemas: An optional list of tool schemas that the model can choose to call.
        :type tool_schemas: typing.Optional[typing.List[ToolSchema]]
        :param kwargs: Additional keyword arguments to pass directly to the
                       `openai.chat.completions.create` method (e.g., `temperature`,
                       `max_tokens`, `response_format`).
        :type kwargs: typing.Any
        :return: The raw ChatCompletion object from the OpenAI API.
        :rtype: openai.types.chat.ChatCompletion
        :raises openai.APIError: If the OpenAI API returns an error.
        :raises ValueError: If `model_name` is not set.
        """
        if not self.model_name:
            raise ValueError(
                "OpenAIModel model_name is not set. Cannot make API calls."
            )

        # Prepend system messages if provided
        final_messages: List[ChatMessage] = (systems if systems else []) + messages

        # Filter out None for tool_schemas if it's explicitly passed as None
        api_tools = (
            tool_schemas if tool_schemas is not None else None
        )  # Pass None if empty, not an empty list

        request_params = {
            "model": self.model_name,
            "messages": final_messages,
        }
        if api_tools:
            request_params["tools"] = api_tools

        # Merge any additional kwargs
        request_params.update(kwargs)

        logger.debug(
            f"Request to model [{self.model_name}]: {json.dumps(request_params, indent=2, default=str)}"
        )
        start_time = time.time()
        try:
            response: ChatCompletion = self.client.chat.completions.create(
                **request_params
            )
            cost_seconds = time.time() - start_time
            # Be cautious logging the full response if it's very large or contains sensitive data.
            # Log relevant parts like usage and finish_reason.
            response_summary = {
                "id": response.id,
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason
                if response.choices
                else "N/A",
                "usage": response.usage.model_dump() if response.usage else "N/A",
            }
            logger.debug(
                f"Response from model [{self.model_name}] received in {cost_seconds:.2f}s. Summary: {json.dumps(response_summary)}"
            )
            return response
        except Exception as e:
            logger.error(
                f"Request to model [{self.model_name}] failed: {e}", exc_info=True
            )  # exc_info for stack trace
            raise  # Re-raise the original exception to be handled by caller or retry logic
