from abc import ABC, abstractmethod
from typing import Any


class AbstractModel(ABC):
    """
    Abstract base class for language models or other generative models.

    This class defines a generic interface for interacting with different
    model implementations. It mandates a `create` method, which is expected
    to be the primary entry point for generating responses or content from
    the model.
    """

    @abstractmethod
    def create(self, *args: Any, **kwargs: Any) -> Any:
        """
        Generates a response or output from the model.

        This is the core abstract method that concrete model implementations
        must provide. The specific arguments (`*args`, `**kwargs`) and the
        structure of the return value (`-> Any`) are intentionally left generic
        to accommodate various types of models and their diverse APIs.

        Implementations should clearly document their specific parameters
        and the format of their return objects.

        :param args: Positional arguments to be passed to the model's generation logic.
        :type args: typing.Any
        :param kwargs: Keyword arguments to be passed to the model's generation logic.
        :type kwargs: typing.Any
        :return: The output from the model. The exact type and structure will
                 depend on the specific model implementation.
        :rtype: typing.Any
        """
        pass
