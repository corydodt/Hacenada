"""
Abstract types
"""
from abc import ABC, abstractmethod

from hacenada.const import STR_DICT


class SessionStorage(ABC):
    """
    Provide access to the session's underlying storage through any mechanism
    """

    @property  # type: ignore
    @abstractmethod
    def description(self):
        """
        A description of this hacenada session
        """

    @description.setter  # type: ignore
    @abstractmethod
    def description(self, val):
        """
        Set the description
        """

    @abstractmethod
    def save_answer(self, answer: STR_DICT):
        """
        Save a single answer
        """

    @abstractmethod
    def update_meta(self, **kw):
        """
        Update meta properties based on keywords (e.g. description="hello world")
        """

    @abstractmethod
    def get_answer(self, label: str):
        """
        Look up a single answer by str
        """


class Render(ABC):
    """
    Rendering operations for question types
    """

    @abstractmethod
    def render(self, step, context) -> STR_DICT:
        """
        Output a question to a device, should return a 0-item label:value dict
        """
