"""
Render (or execute) steps
"""
import PyInquirer as pyinquirer


## from hacenada.inquireradapter import ConsoleRenderCustom


class StopRendering(Exception):
    """
    Indicates that a step wants to stop execution and save

    i.e. step['stop'] == True
    """

    def __init__(self, step):
        self.step = step


def _adapt_answers(answers_list):
    """
    Convert our answers list into an answers dict which pyinquirer can use
    """
    return {k: v for answer in answers_list for (k, v) in answer.items()}


class Render:
    """
    Rendering operations for question types
    """

    def _inquirer_type(self, typename):
        """
        Return the inquirer question type for the given type name
        """
        return {
            "description": "input",
            "editor": "editor",
            "message": "confirm",
            "confirm": "confirm",
        }[typename]

    def render(self, step, context):
        """
        Output a question to a device
        """
        pyinq_type = self._inquirer_type(step["type"])

        if context.description:
            title = f"{context.description} : {step['label']}"
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
        _pyinq_answers = _adapt_answers(context.answers)
        ret = pyinquirer.prompt(questions=qs, answers=_pyinq_answers)

        return ret
