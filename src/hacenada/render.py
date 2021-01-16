"""
Render (or execute) steps
"""
import typing

import inquirer

from hacenada.abstract import Render
from hacenada.const import STR_DICT
from hacenada.script import Step
from hacenada.session import Session


class InquirerRender(Render):
    """
    Render to console using inquirer
    """

    @staticmethod
    def _inquirer_dispatch(typename: str) -> typing.Callable:
        """
        Return the inquirer question type for the given type name
        """
        functions = {
            "description": "text",
            "input": "text",
            "message": "confirm",
            "confirm": "confirm",
            # "editor": "editor",
            # "choice": "choice",
            # "password": "password",
        }

        return getattr(inquirer, functions[typename])

    def render(self, step: Step, context: Session) -> STR_DICT:
        """
        Output a question to a device
        """
        pyinq_prompt = self._inquirer_dispatch(step["type"])

        if context.storage.description:
            title = f"{context.storage.description} : {step['label']}"
        else:
            title = f"{context.script.preamble['name']} : {step['label']}"

        message = f"{title}\n" f"{step['message']}\n>>"

        answered = pyinq_prompt(message)

        # FIXME: just return an Answer here
        return {step["label"]: answered}
