"""
Write do-nothing scripts, inspired by
https://blog.danslimmon.com/2019/07/15/do-nothing-scripting-the-key-to-gradual-automation/

(From the Spanish, "hace nada" meaning "it does nothing")

    1. Load a template from the input file
    2. prompt for a description (optional)
    3. display the description and display the next question from .hacenada.tpl
    4. if the question is answered in a certain way (or at all), save to .hacenada.step
    5. exit

    6. on the next run, look for .hacenada.step. if it doesn't exist we're starting at step 1.
    7. if we have .hacenada.step, look up the next step
    8. if there is a next step, repeat at step 3.
    9. if not, we're done. write a log file:
        - create hacenada-logs
        - add a file there that uses the date and description field as the logfile name
        - write a human-readable description of what happened to that log


    - should be able to mark fields as passwords/secrets (hidden in log)
    - should be able to say a text field is required (e.g. you must put in a username before it continues)
    - can automate a step away completely

    - how to establish continuity between versions, e.g. if a template has changed from one run to the next
        (probably encode a version of the original template into the .hacenada.step file)
    - --start-over will let you discard a run in process. this writes the (incomplete) log to the logs dir as
        if you had finished.
    - use codado.hotedit for interactive editor steps

    - challenges: it needs to be easy/lightweight for an operator to run a script. The script already
      imports several third-party libraries and I haven't even written any code yet.
      minimize dependencies or have a canonical way (like a curl-pipe-bash installer?)

      Could also be a snap install!
"""
import json
import pathlib

import click
import toml

from hacenada import render, script, session, storage


def handle_filename(_, param, value):
    """
    Process the filename argument

    Raise a UsageError when the file is missing unless the param has default=None
    """
    if value is None:
        if not param.required:
            return None
        raise click.UsageError("** FILENAME is required")

    value = pathlib.Path(value)
    if not param.required:
        return value

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
    if filename:
        _store = storage.HomeDirectoryStorage.from_path(filename)
    else:
        _store = storage.HomeDirectoryStorage.from_cwd()
        filename = _store.script_path

    _opt = session.SessionOptions(renderer=render.PyInquirerRender())
    _script = script.Script.from_scriptfile(filename)
    sesh = session.Session(script=_script, storage=_store, options=_opt)

    sesh.step_session()


@hacenada.command()
@click.option("--start-over", "starting_over", is_flag=True)
@filename_arg()
def start(filename, starting_over):
    """
    Begin a new session after opening filename.
    """
    _store = storage.HomeDirectoryStorage.from_path(filename)
    if starting_over:
        _store.drop()
        _store = storage.HomeDirectoryStorage.from_path(filename)

    _script = script.Script.from_scriptfile(filename)
    _opt = session.SessionOptions(renderer=render.PyInquirerRender())
    sesh = session.Session(script=_script, storage=_store, options=_opt)
    if sesh.started and not starting_over:
        raise click.UsageError(
            f"** {_store} already contains some answers, will not overwrite an ongoing session without --start-over"
        )

    sesh.step_session()


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

    if filename:
        _store = storage.HomeDirectoryStorage.from_path(filename)
    else:
        _store = storage.HomeDirectoryStorage.from_cwd()
        filename = _store.script_path

    _script = script.Script.from_scriptfile(filename)

    from hacenada import main
    printer = getattr(main, f"print_{format}")
    printer(_script, _store)


def print_toml(script, storage):
    print(toml.dumps({"hacenada": script.preamble}))
    print(toml.dumps({"step": script.raw_steps}))
    print(toml.dumps({"answer": storage.answer.all()}))


def print_json(script, storage):
    ret = dict(
        hacenada=script.preamble,
        step=script.raw_steps,
        answer=storage.answer.all(),
    )
    print(json.dumps(ret, indent=2))


def print_markdown(script, storage):
    """
    Markdown formatting interleaves questions with answers to produce a human-readable document
    """
    print(f"# {script.preamble['name'] or storage.script_path}\n")
    print(f"{script.preamble['description'] or ''}\n")
    if storage.description:
        desc = storage.description.replace('\n', ' ').strip()
        print(f"### Current: **{desc}**\n")

    print("## Steps\n")
    for step in script.overlay:
        label = step["label"]
        print(f"[{label}]  {step['message'].strip()}\n")
        # TODO: depending on step['type'], format and print interactive choices

        _answered = storage.get_answer(label)
        if _answered:
            print(f"➡️➡️**{_answered['value']}**\n")

        if step["stop"]:
            print("------\n")
