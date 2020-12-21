"""
Render (or execute) steps
"""

import inquirer

from hacenada.inquireradapter import ConsoleRenderCustom


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
            "description": inquirer.Text,
            "editor": inquirer.Editor,
            "message": inquirer.Confirm,
            "confirm": inquirer.Confirm,
        }[typename]

    def render(self, step, context):
        """
        Output a question to a device
        """
        clz = self._inquirer_type(step["type"])

        qs = [clz(name=step["label"], message=step["message"])]

        inquirer.prompt(qs, answers=context)  # render=ConsoleRenderCustom)

        if step["stop"]:
            raise StopRendering(step)
