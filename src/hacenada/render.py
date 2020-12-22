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

        message = (
            f"{context.script.preamble['name']} : {step['label']}\n"
            f"{step['message']}\n"
        )

        qs = [dict(
            name=step["label"],
            message=message,
            type=pyinq_type,
        )]

        pyinquirer.prompt(questions=qs, answers=context.answers)

        if step["stop"]:
            raise StopRendering(step)
