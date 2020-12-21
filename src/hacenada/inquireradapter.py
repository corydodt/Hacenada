"""
Adapter for hotedit.hotedit to use in place of inquirer.Editor
"""
from codado import hotedit
import inquirer
from inquirer.render.console import ConsoleRender
from inquirer.render.console import Editor as EditorRender
from readchar import key


class HotEdit(EditorRender):
    """
    A text question that uses hotedit.hotedit as the implementation

    Works almost identically to the standard inquirer.Editor but uses a
    different underlying implementation that does a better job with
    modern editor invocation.
    """

    def process_input(self, pressed):
        if pressed == key.CTRL_C:
            raise KeyboardInterrupt()

        if pressed in (key.CR, key.LF, key.ENTER):
            data = hotedit.hotedit(self.question.default or "")
            raise inquirer.errors.EndOfInput(data)

        raise inquirer.errors.ValidationError(
            "You have pressed an unknown key! Press <enter> to open editor or CTRL+C to exit."
        )


class ConsoleRenderCustom(ConsoleRender):
    """
    A Render that uses HotEdit in place of python-editor's implementation
    """

    def render_factory(self, question_type):
        if question_type == "editor":
            return HotEdit

        return super().render_factory(question_type)
