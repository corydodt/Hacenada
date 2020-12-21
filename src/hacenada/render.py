"""
Render (or execute) steps
"""

import inquirer

from hacenada.inquireradapter import ConsoleRenderCustom


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
        }[typename]

    def render(self, context, step):
        """
        Output a question to a device
        """
        clz = self._inquirer_type(step["type"])

        qs = [clz("hello")]

        inquirer.prompt(qs)  # render=ConsoleRenderCustom)
