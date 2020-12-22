"""
Read/write from the .session file, manage which step we're on, manage logs
"""
import io
import json
import pathlib
import re
import tarfile
import tempfile

import attr

from hacenada import render
from hacenada.script import Script


ENCODING = "utf8"


def log(msg):
    print(f"✨ {msg}")


class MissingScriptError(Exception):
    """
    Failed to find the script file to initialize a session
    """

    def __init__(self, path: pathlib.Path, message: str = ""):
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
    renderer: render.Render = attr.Factory(render.Render)
    description: str = ""

    SCRIPT_FROM_SESSION_RX = re.compile(r"\.(.+?)\.session.tgz")

    @property
    def session_path(self):
        """
        Derive session_path from script_path
        """
        return self.get_session_path(self.script_path)

    @staticmethod
    def get_session_path(script_path: pathlib.Path, create=False):
        """
        Using the path to the script_file, determine the location of the session file and return it

        -> None if the session file does not exist
        """
        return pathlib.Path(f"{script_path.parent}/.{script_path.stem}.session.tgz")

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
        _missing = MissingScriptError(
            None, f"no hacenada sessions (*.session.tgz) found in {cwd}"
        )
        _multiple = MissingScriptError(
            None,
            f"more than 1 hacenada session found in {cwd}; instead, please run: hacenada next <script_file>",
        )

        sessions = list(cwd.glob(".*.session.tgz"))
        if len(sessions) > 1:
            raise _multiple

        if not sessions:
            raise _missing

        session_file = str(sessions[0])

        parsed = cls.SCRIPT_FROM_SESSION_RX.match(session_file)
        if not parsed.group(1):
            raise _missing

        script_path = pathlib.Path(f"{parsed.group(1)}.toml")
        ret = cls.from_filename(script_path)

        log(f"guessed {script_path}")
        return ret

    @property
    def started(self):
        return self.session_path.exists()

    def start(self, create=False):
        """
        Begin a session, loading from disk if possible
        """
        self.script = Script.from_scriptfile(self.script_path)

        if create:
            # save an empty answer list so we can immediately load
            self.save()

        self.load()

    def step_session(self):
        """
        Advance the session to the next question step, render, and collect the answer
        """
        assert (
            self.started
        ), f"doing step_session but {self.session_path} does not exist"
        assert self.script, "doing step_session but start() was not called"

        index = len(self.answers)
        remaining = self.script.overlay[index:]

        for step in remaining:
            answer = self.renderer.render(step, context=self)
            self.answers.append(answer)
            posthandler = getattr(self, f"post_{step['type']}", lambda *a: None)
            posthandler(step["label"], step["type"], answer[step["label"]])
            self.save()
            if step["stop"]:
                break

        print("---------------")

    def post_description(self, _, __, value):
        """
        Set the description attribute
        """
        self.description = value

    def to_structured(self):
        """
        A structured representation
        """

        def serialize(inst, field, value):
            if isinstance(value, pathlib.Path):
                return value.name
            if isinstance(value, Script):
                return value.to_structured()
            return value

        return attr.asdict(
            self,
            filter=attr.filters.exclude(render.Render),
            value_serializer=serialize,
        )

    def load(self):
        td = tempfile.TemporaryDirectory()
        try:
            tar = tarfile.open(self.session_path, "r:gz")
            tar.extractall(td.name)
            with open(f"{td.name}/{self.script_path.stem}.d/session.json") as f:
                session_data = json.load(f)
                self.answers = session_data["answers"]
                self.description = session_data["description"]
                orig_script = Script.from_structured(session_data["script"])
                assert (
                    orig_script == self.script
                ), "The script file has changed since last save! Retry with --use-saved-script"
            log(f"loaded {self.session_path}")
        finally:
            td.cleanup()

    def save(self):
        """
        Commit all session info to a file
        """
        td = tempfile.TemporaryDirectory()
        try:
            tar = tarfile.open(f"{td.name}/session.tgz", "w:gz")

            tar.addfile(
                *package_tar_data(
                    self.to_structured(),
                    f"{self.script_path.stem}.d/session.json",
                )
            )
            tar.close()

            pathlib.Path(tar.name).rename(self.session_path)
            log(f"saved {self.session_path}")
        finally:
            td.cleanup()


def package_tar_data(data, filename: str):
    """
    A (TarInfo, fileobj) for the given data, after json- and utf8-encoding it.
    """
    ti = tarfile.TarInfo(name=filename)
    encoded = json.dumps(data, indent=2, sort_keys=True).encode(ENCODING)
    byte_f = io.BytesIO()
    byte_f.write(encoded)
    ti.size = byte_f.tell()
    byte_f.seek(0)
    return (ti, byte_f)
