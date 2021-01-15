"""
Script parser and understander
"""
import typing

import attr
import toml

from hacenada import compat


class Step(compat.TypedDict):
    type: str
    message: str
    label: str
    stop: bool


@attr.s(auto_attribs=True)
class Script:
    """
    Structured hacenada script representation from parsing a .toml script
    """

    preamble: dict = attr.Factory(dict)
    raw_steps: list = attr.Factory(list)
    overlay: list = attr.Factory(list)  # steps after preprocessing

    @staticmethod
    def autolabel(step, n):
        return f'{step["type"]}-{n}'

    def preprocess_steps(self, steps: typing.List[typing.Dict]) -> typing.List[Step]:
        """
        Run a preprocessor on each step, setting defaults and such.
        """
        overlay = []
        for n, item in enumerate(steps):
            step = Step(
                type=item.get("type", "message"),
                message=item["message"],
                stop=item.get("stop", True),
                label=item.get("label", ""),
            )

            if not step["label"]:
                step["label"] = self.autolabel(step, n)

            overlay.append(step)

        return overlay

    @classmethod
    def from_scriptfile(cls, scriptfile):
        """
        Constructor, creates a Script() instance from a filename containing .toml
        """
        with open(scriptfile) as f:
            data = toml.load(f)

        return cls.from_structured(data)

    @classmethod
    def from_structured(cls, data):
        """
        Constructor, creates from structured data
        """
        self = cls()
        self.raw_steps = data["step"]
        self.overlay = self.preprocess_steps(data["step"])
        self.preamble = data["hacenada"]
        return self
