"""
Script parser and understander
"""

import attr
import toml


@attr.s
class Script:
    """
    Structured hacenada script representation from parsing a .toml script
    """

    preamble: dict = attr.Factory(dict)
    steps: list = attr.Factory(list)

    @classmethod
    def from_scriptfile(cls, scriptfile):
        """
        Constructor, creates a Script() instance from a filename
        """
        self = cls()
        with open(scriptfile) as f:
            data = toml.load(f)

        self.steps = data["step"]
        self.preamble = data["hacenada"]
        return self

    def to_structured(self):
        """
        A structured-data representation of the script
        """
        return {"hacenada": self.preamble, "step": self.steps}
