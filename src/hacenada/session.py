"""
Read/write from the .session file, manage which step we're on, manage logs
"""

import attr

from hacenada import render
from hacenada.script import Script
from hacenada.abstract import SessionStorage


@attr.s(auto_attribs=True)
class SessionOptions:
    """
    Options for a Session
    """

    renderer: render.Render


@attr.s(auto_attribs=True, slots=True)
class Session:
    """
    The state as we answer the script questions
    """

    storage: SessionStorage
    script: Script
    options: SessionOptions

    @property
    def started(self):
        return len(self.storage.answer) > 0

    def step_session(self):
        """
        Advance the session to the next question step, render, and collect the answer
        """
        index = len(self.storage.answer)
        remaining = self.script.overlay[index:]

        for step in remaining:
            q_a = self.options.renderer.render(step, context=self)
            self.storage.save_answer(q_a)
            posthandler = getattr(self, f"post_{step['type']}", lambda *a: None)
            posthandler(step["label"], step["type"], q_a[step["label"]])
            if step["stop"]:
                break

        print("---------------")

    def post_description(self, _, __, value):
        """
        Set the description attribute
        """
        self.storage.description = value
