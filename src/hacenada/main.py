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
import pathlib

import click

from hacenada import session


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
    try:
        if filename:
            sesh = session.Session.from_filename(filename)
        else:
            sesh = session.Session.from_guessed_filename()
    except session.MissingScriptError as e:
        raise click.UsageError(str(e))

    sesh.start(create=False)
    sesh.step_session()


@hacenada.command()
@click.option("--start-over", "starting_over", is_flag=True)
@filename_arg()
def start(filename, starting_over):
    """
    Begin a new session after opening filename.
    """
    sesh = session.Session.from_filename(filename)
    if sesh.started and not starting_over:
        raise click.UsageError(
            f"** {sesh.session_path} exists, will not overwrite an ongoing session without --start-over"
        )

    sesh.start(create=True)
    sesh.step_session()


FORMAT_CHOICES = ("toml", "json", "markdown")


@hacenada.command("print")
@filename_arg()
@click.option("--format", default="toml", type=click.Choice(FORMAT_CHOICES))
@click.option("--answers/--no-answers", "with_answers", default=True)
def print_script(filename, format, with_answers):
    """
    Print the question script in a readable format

    With --answers (the default), include the answers from the current session
    """
    raise NotImplementedError()
