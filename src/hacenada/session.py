"""
Read/write from the .session file, manage which step we're on, manage logs
"""
from __future__ import annotations

import attr

from hacenada import error
from hacenada.abstract import Render, SessionStorage
from hacenada.script import Script


@attr.s(auto_attribs=True)
class SessionOptions:
    """
    Options for a Session
    """

    renderer: Render


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
        """
        Have we previously started this session (there are previous answers?)
        """
        return len(self.storage.answer) > 0

    def step_session(self):
        """
        Advance the session to the next question step, render, and collect the answer
        """
        index = len(self.storage.answer)
        remaining = self.script.overlay[index:]

        while remaining:
            step = remaining.pop(0)
            try:
                q_a = self.options.renderer.render(step, context=self)
            except error.Unanswered:
                print(f"** Canceled at {step['label']}")
                return

            self.storage.save_answer(q_a)
            posthandler = getattr(self, f"post_{step['type']}", lambda *a: None)
            posthandler(step["label"], step["type"], q_a[step["label"]])
            if step["stop"]:
                break

        # did we reach the end?
        if len(remaining) == 0:
            raise error.ScriptFinished("all steps have been seen")

        print("---------------")

    def post_description(self, _, __, value):
        """
        Set the description attribute
        """
        self.storage.description = value
