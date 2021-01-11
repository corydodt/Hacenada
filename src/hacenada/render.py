"""
Render (or execute) steps
"""
import PyInquirer as pyinquirer

from hacenada import error
from hacenada.abstract import Render
from hacenada.const import STR_DICT
from hacenada.script import Step
from hacenada.session import Session


class PyInquirerRender(Render):
    """
    Render to console using pyinquirer
    """

    @staticmethod
    def _inquirer_type(typename: str) -> str:
        """
        Return the inquirer question type for the given type name
        """
        return {
            "description": "input",
            "editor": "editor",
            "message": "confirm",
            "confirm": "confirm",
        }[typename]

    def render(self, step: Step, context: Session) -> STR_DICT:
        """
        Output a question to a device
        """
        pyinq_type = self._inquirer_type(step["type"])

        if context.storage.description:
            title = f"{context.storage.description} : {step['label']}"
        else:
            title = f"{context.script.preamble['name']} : {step['label']}"

        message = f"{title}\n" f"{step['message']}\n>>"

        qs = [
            dict(
                name=step["label"],
                message=message,
                type=pyinq_type,
            )
        ]
        _pyinq_answers: STR_DICT = {}  # TODO
        pyinq_answers = pyinquirer.prompt(questions=qs, answers=_pyinq_answers)

        answered = pyinq_answers.get(step["label"])
        if answered is None:
            raise error.Unanswered(f"{step['label']} not answered - User Canceled?")

        return {step["label"]: pyinq_answers[step["label"]]}
