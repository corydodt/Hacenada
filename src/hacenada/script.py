"""
Script parser and understander
"""
import typing

import attr
import toml


class Step(typing.TypedDict, total=False):
    type: str
    message: str
    label: typing.Union[str, None]
    stop: bool


@attr.s
class Script:
    """
    Structured hacenada script representation from parsing a .toml script
    """

    preamble: dict = attr.Factory(dict)
    raw_steps: list = attr.Factory(list)
    overlay: list = attr.Factory(list)  # steps after preprocessing

    def autolabel(self, step, n):
        return f'{step["type"]}-{n}'

    def preprocess_steps(self, steps: typing.List[typing.Dict]) -> typing.List[Step]:
        """
        Run a preprocessor on each step, setting defaults and such.
        """
        overlay = []
        for n, item in enumerate(steps):
            step = Step(**item)
            step.setdefault("type", "message")
            step.setdefault("stop", True)

            step.setdefault("label", self.autolabel(step, n))

            overlay.append(step)

        return overlay

    @classmethod
    def from_scriptfile(cls, scriptfile):
        """
        Constructor, creates a Script() instance from a filename
        """
        self = cls()
        with open(scriptfile) as f:
            data = toml.load(f)

        self.raw_steps = data["step"]
        self.overlay = self.preprocess_steps(data["step"])
        self.preamble = data["hacenada"]
        return self

    def to_structured(self):
        """
        A structured-data representation of the script
        """
        return {"hacenada": self.preamble, "step": self.raw_steps}
