"""
Read/write from the .session file, manage which step we're on, manage logs
"""
import io
import json
import os
import pathlib
import re
import tarfile
import tempfile

import attr
import toml

from hacenada.render import Render
from hacenada.script import Script


ENCODING = "utf8"


def log(msg):
    print(f"✨{msg}")


class MissingScriptError(Exception):
    """
    Failed to find the script file to initialize a session
    """

    def __init__(self, path, message=""):
        self.path = path
        self.message = message or f"{path} missing"

    def __str__(self):
        return self.message or self.path


@attr.s(auto_attribs=True)
class Session:
    """
    The state as we answer the script questions
    """

    script_path: pathlib.Path = attr.ib(converter=pathlib.Path)
    script: Script = None
    answers: list = attr.Factory(list)
    renderer: Render = attr.Factory(Render)

    SCRIPT_FROM_SESSION_RX = re.compile(r"\.(.+?)\.session")

    @property
    def session_path(self):
        """
        Derive session_path from script_path
        """
        return self.get_session_path(self.script_path)

    @staticmethod
    def get_session_path(script_path, create=False):
        """
        Using the path to the script_file, determine the location of the session file and return it

        -> None if the session file does not exist
        """
        return pathlib.Path(f"{script_path.parent}/.{script_path.name}.session")

    @classmethod
    def from_filename(cls, script_file):
        """
        Constructor, return Session initialized with the script_file
        """
        script_path = pathlib.Path(script_file)
        if not script_path.exists():
            raise MissingScriptError(script_path)

        sesh_path = cls.get_session_path(script_path)
        self = cls(script_path, sesh_path)
        log(f"created Session from {sesh_path}")
        return self

    @classmethod
    def from_guessed_filename(cls):
        """
        Constructor, attempt to guess the script file by looking for a .session file in the cwd

        Fails if:
            - there is no .session file
            - more than one .session file exists, or
            - a .session file was found but it doesn't match any script file

        Otherwise returns a new Session instance
        """
        cwd = pathlib.Path(".")
        _missing = MissingScriptError(None, f"no hacenada sessions found in {cwd}")
        _multiple = MissingScriptError(
            None,
            f"more than 1 hacenada session found in {cwd}; instead, please run: hacenada next <script_file>",
        )

        sessions = list(cwd.glob(".*.session"))
        if len(sessions) > 1:
            raise _multiple

        if not sessions:
            raise _missing

        session_file = str(sessions[0])

        parsed = cls.SCRIPT_FROM_SESSION_RX.match(session_file)
        if not parsed.group(1):
            raise _missing

        script_path = pathlib.Path(parsed.group(1))
        ret = cls.from_filename(script_path)

        log(f"guessed {script_path}")
        return ret

    @property
    def started(self):
        return self.session_path.exists()

    def start(self, create=False):
        """
        Begin a session
        """
        if create:
            self.session_path.open("w").close()

        self.script = Script.from_scriptfile(self.script_path)

        log("starting")

    def step_session(self):
        """
        Advance the session to the next question step, render, and collect the answer
        """
        assert (
            self.started
        ), f"doing step_session but {self.session_path} does not exist"
        assert self.script, "doing step_session but start() was not called"

        index = len(self.answers)
        step = self.script.steps[index]

        response = self.renderer.render(context=self.answers, step=step)
        self.answers.append(response)

        self.save()

        ## exiting = False
        ## while not exiting:
        ##     response = self.render(context=self.answers, step)
        ##     exiting = True if not step.disable_break else False

        log("finished steps")

    def save(self):
        """
        Commit all session info to a file
        """
        td = tempfile.TemporaryDirectory()
        try:
            tar = tarfile.open(f"{td.name}/session.tar", "w:gz")
            session_obj = bytesio_from_data({"session": self.answers})
            script_obj = bytesio_from_data({"script": self.script.to_structured()})
            tar.addfile(
                tarfile.TarInfo(name=f"{self.script_path.name}.d/session.json"),
                session_obj,
            )
            tar.addfile(
                tarfile.TarInfo(name=f"{self.script_path.name}.d/script.json"),
                script_obj,
            )

            pathlib.Path(tar.name).rename(self.session_path)
            log("saved")
        finally:
            td.cleanup()


def bytesio_from_data(data):
    """
    A new BytesIO object with the contents of `data`, JSON- and UTF8-encoded

    -> new open fileobj with the data
    """
    bytes = json.dumps(data).encode(ENCODING)
    byte_f = io.BytesIO()
    byte_f.write(bytes)
    return byte_f
