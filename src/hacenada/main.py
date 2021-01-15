"""
Write do-nothing scripts, inspired by
https://blog.danslimmon.com/2019/07/15/do-nothing-scripting-the-key-to-gradual-automation/

(From the Spanish, "hace nada" meaning "it does nothing")

    1. Load a template from the input file
    2. prompt for a description (optional)
    3. display the description and display the next question from .hacenada.tpl
    4. if the question is answered in a certain way (or at all), save to a home directory storage db
    5. exit

    6. on the next run, look for the storage db and continue.
    7. if there is a next step, repeat at step 3.
    8. if not, we're done. write a log file:
        - create template-filename.log.d/{date}-{n}--{description}.log
        - write two log versions: markdown and json

    - should be able to mark fields as passwords/secrets (hidden in log)
    - should be able to say a text field is required (e.g. you must put in a username before it continues)
    - can automate a step away completely

    - --start-over will let you discard a run in process. this writes the (incomplete) log to the logs dir as
        if you had finished.

    - challenges: it needs to be easy/lightweight for an operator to run a script. The script already
      imports several third-party libraries and I haven't even written any code yet.
      minimize dependencies or have a canonical way (like a curl-pipe-bash installer?)
"""
import datetime
import io
import json
import pathlib
import typing
import urllib

import click
import toml

from hacenada import render, script, session, storage
from hacenada.abstract import SessionStorage
from hacenada.error import ScriptFinished, StorageError


def handle_filename(_, param, value):
    """
    Process the filename argument

    Raise a UsageError when the file is missing unless the param is not required
    """
    if value is None:
        if not param.required:
            return None
        raise click.UsageError("** FILENAME is required")

    value = pathlib.Path(value)

    if value.exists():
        return value

    raise click.UsageError(f"** {value} does not exist :(")


def filename_arg(*args, **kwargs):
    """
    Common decorator argument for the filename
    """
    return click.argument("filename", callback=handle_filename, *args, **kwargs)


@click.group()
def hacenada():
    """
    Top-level command for hacenada
    """


def _find_storage_somehow(filename) -> typing.Tuple[pathlib.Path, SessionStorage]:
    """
    With no filename argument given, try to determine storage location
    """
    try:
        if filename:
            return (filename, storage.HomeDirectoryStorage.from_path(filename))
        else:
            _store = storage.HomeDirectoryStorage.from_cwd()
            return (pathlib.Path(_store.script_path), _store)
    except StorageError as e:
        raise click.UsageError(str(e))


@hacenada.command()
@filename_arg(required=False)
def next(filename):
    """
    Run the next step.

    With FILENAME given, look for a continuation file matching that filename
    (and error if none is found).

    With no FILENAME, look for any continuation file, and continue it.
    This is an error if there are multiple continuation files, or none.
    """
    filename, _store = _find_storage_somehow(filename)

    _opt = session.SessionOptions(renderer=render.PyInquirerRender())
    _script = script.Script.from_scriptfile(filename)
    sesh = session.Session(script=_script, storage=_store, options=_opt)

    try:
        sesh.step_session()
    except ScriptFinished:
        _log_and_cleanup(sesh)


@hacenada.command()
@click.option("--start-over", "starting_over", is_flag=True)
@filename_arg()
def start(filename, starting_over):
    """
    Begin a new session after opening filename.
    """
    if starting_over:
        storage.HomeDirectoryStorage.drop_path(filename)
    _store = storage.HomeDirectoryStorage.from_path(filename)

    _script = script.Script.from_scriptfile(filename)
    _opt = session.SessionOptions(renderer=render.PyInquirerRender())
    sesh = session.Session(script=_script, storage=_store, options=_opt)
    if sesh.started and not starting_over:
        raise click.UsageError(
            f"** <{filename}-storage> already contains some answers, "
            "will not overwrite an ongoing session without --start-over"
        )

    try:
        sesh.step_session()
    except ScriptFinished:
        _log_and_cleanup(sesh)


FORMAT_CHOICES = ("toml", "json", "markdown")


@hacenada.command("print")
@filename_arg(required=False)
@click.option("--format", default="toml", type=click.Choice(FORMAT_CHOICES))
@click.option("--answers/--no-answers", "with_answers", default=True)
def print_script(filename, format, with_answers):
    """
    Print the question script in a readable format

    With --answers (the default), include the answers from the current session
    """

    if with_answers:
        filename, _store = _find_storage_somehow(filename)
    else:
        _store = None

    _script = script.Script.from_scriptfile(filename)

    from hacenada import main

    formatter = getattr(main, f"format_{format}")
    print(formatter(_script, _store))


def format_toml(script: script.Script, storage: SessionStorage) -> str:
    """
    Format the steps and answers as TOML
    """
    _io = io.StringIO()
    print(toml.dumps({"hacenada": script.preamble}), file=_io)
    print(toml.dumps({"step": script.raw_steps}), file=_io)
    if storage:
        print(toml.dumps({"answer": storage.answer.all()}), file=_io)

    return _io.getvalue()


def format_json(script: script.Script, storage: SessionStorage) -> str:
    """
    Format the steps and answers as json
    """
    ret = dict(
        hacenada=script.preamble,
        step=script.raw_steps,
    )
    if storage:
        ret["answer"] = storage.answer.all()
    return json.dumps(ret, indent=2, default=_json_default_datetime)


def _json_default_datetime(o):
    """
    Json dumper for datetimes
    """
    if isinstance(o, datetime.datetime):
        return o.isoformat()
    raise TypeError(f"can't encode {o!r}")  # pragma: nocover


def format_markdown(script: script.Script, storage: SessionStorage) -> str:
    """
    Form steps and answers as markdown

    Markdown formatting interleaves questions with answers to produce a
    human-readable document
    """
    _io = io.StringIO()
    print(f"# {script.preamble['name'] or storage.script_path}\n", file=_io)
    print(f"{script.preamble['description'] or ''}\n", file=_io)
    if storage and storage.description:
        desc = storage.description.replace("\n", " ").strip()
        print(f"### Current: **{desc}**\n", file=_io)

    print("## Steps\n", file=_io)
    for step in script.overlay:
        label = step["label"]
        print(f"[{label}]  {step['message'].strip()}\n", file=_io)
        # TODO: depending on step['type'], format and print interactive choices

        if storage:
            _answered = storage.get_answer(label)
            if _answered:
                local_when = _answered["when"].astimezone().ctime()
                print(f"**>> {_answered['value']} <<** ({local_when})\n", file=_io)

        if step["stop"]:
            print("------\n", file=_io)

    return _io.getvalue()


def _log_path(script_path: pathlib.Path, description: str) -> pathlib.Path:
    """
    What filename will the log for this session have?
    """
    logd_path = script_path.with_suffix(".log.d")
    logd_path.mkdir(exist_ok=True)
    dt = datetime.date.today().isoformat()
    counter = len(list(logd_path.glob(f"{dt}*.log"))) + 1
    # make the description more url-like
    desc = urllib.parse.quote_plus(" ".join(description.split()))

    return logd_path / f"{dt}-{counter}--{desc}.log"


def _log_and_cleanup(sesh: session.Session):
    """
    When done, write some logs and drop the db
    """
    log_md = format_markdown(sesh.script, sesh.storage)
    fn_md = _log_path(sesh.storage.script_path, sesh.storage.description)
    fn_md.write_text(log_md)
    log_json = format_json(sesh.script, sesh.storage)
    fn_json = fn_md.with_suffix(".json")
    fn_json.write_text(log_json)

    print(f"{sesh.storage.script_path}: Cleaning up.  Log: {fn_md}")
    sesh.storage.drop()
