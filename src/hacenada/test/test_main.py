"""
Test the command-line for regressions
"""
import pathlib
import re
from unittest.mock import Mock, patch

import click
from click.testing import CliRunner
from pytest import fixture, mark, raises

from hacenada import main, error


@fixture
def runner() -> CliRunner:
    return CliRunner()


def test_handle_filename(my_project):
    """
    Do we correctly handle click params for the filename, including error conditions?
    """
    required = Mock(required=True)
    not_required = Mock(required=False)

    with raises(click.UsageError):
        main.handle_filename(Mock(), required, None)

    assert main.handle_filename(Mock(), not_required, None) is None

    assert main.handle_filename(Mock(), required, "project.toml") == pathlib.Path(
        "project.toml"
    )

    with raises(click.UsageError):
        main.handle_filename(Mock(), required, "project-ohno.toml")


def match_output(output, matcher_id):
    """
    Make an assertion about the output using a regex.

    Look up the matcher from the matcher_id.
    """
    rx = INVOCATION_MATCHERS[matcher_id]
    assert rx.search(output)


INVOCATION_MATCHERS = {
    "print-toml": re.compile(r'^\[hacenada\].*to it"\n\n$', re.M | re.DOTALL),
    "print-json": re.compile(
        r'^{\s+"hacenada":.*to it"\s*}\s*\]\s*}\s*$', re.M | re.DOTALL
    ),
    "print-markdown": re.compile(
        r"^# hola.*oh noo\n\n------\n\n\[message-1\]", re.M | re.DOTALL
    ),
    "print-toml-answers": re.compile(
        r'^\[hacenada\].*\[\[answer\]\]\nlabel = "q1"', re.M | re.DOTALL
    ),
    "print-json-answers": re.compile(
        r'^{\s+"hacenada":.*to it".*"answer": \[\s*{\s*"label".*$', re.M | re.DOTALL
    ),
    "print-markdown-answers": re.compile(
        r"^# hola.*oh noo\n\n.*\*\*>> hello description <<\*\* \(.*\)\n\n---", re.M | re.DOTALL
    ),
}


@mark.parametrize(
    "cli_args,output_id",
    [
        [["--format=toml", "project.toml", "--no-answers"], "print-toml"],
        [["--format=json", "project.toml", "--no-answers"], "print-json"],
        [["--format=markdown", "project.toml", "--no-answers"], "print-markdown"],
        [["--format=toml", "project.toml", "--answers"], "print-toml-answers"],
        [["--format=json", "project.toml", "--answers"], "print-json-answers"],
        [["--format=markdown", "project.toml", "--answers"], "print-markdown-answers"],
    ],
    ids=[
        "print-toml",
        "print-json",
        "print-markdown",
        "print-toml-answers",
        "print-json-answers",
        "print-markdown-answers",
    ],
)
def test_print(
    cli_args, output_id, runner: CliRunner, my_project: pathlib.Path, storagie
):
    """
    Do I print out a script, both with and without answers?
    Different formats?
    """
    storagie.save_answer({"q1": "hello description"})
    storagie.description = "hello description"
    invoked = runner.invoke(main.print_script, cli_args)
    assert invoked.exit_code == 0, f"{invoked.exit_code} {invoked.exception}"
    match_output(invoked.stdout, output_id)


def test_print_filename_antics(runner: CliRunner, my_project: pathlib.Path, storagie):
    """
    Do we find the right storage when filename arg or actual file is missing?
    """
    storagie.save_answer({"q1": "hello description"})
    cli_args = ["--answers"]

    # this invocation succeeds because storage can be found
    invoked = runner.invoke(main.print_script, cli_args)
    assert invoked.exit_code == 0, f"{invoked.exit_code} {invoked.exception}"
    assert re.search(r"hello description", invoked.stdout)

    storagie.db.close()

    # this invocation fails, storage file has disappeared
    for found in my_project.parent.parent.glob("*.json"):
        found.unlink()
    invoked = runner.invoke(main.print_script, cli_args)
    assert invoked.exit_code > 0
    assert re.search(r"No possible storage found", invoked.stdout)


def test_start(runner: CliRunner, my_project: pathlib.Path):
    """
    Do we handle all the states of starting and starting over?
    """
    p_render = patch(
        "hacenada.render.PyInquirerRender.render",
        autospec=True,
        return_value={"q1": "descriptione"},
    )

    # start with no storage
    with p_render:
        invoked = runner.invoke(main.start, ["project.toml"])
    assert invoked.exit_code == 0, f"{invoked.exit_code} {invoked.exception}"

    # start again after answering 1 question
    invoked = runner.invoke(main.start, ["project.toml"])
    assert "already contains some answers" in invoked.stdout
    assert invoked.exit_code > 0

    # start again but use --start-over
    with p_render:
        invoked = runner.invoke(main.start, ["--start-over", "project.toml"])
    assert invoked.exit_code == 0, f"{invoked.exit_code} {invoked.exception}"

    # start again. this is a hack to make the first question appear to be the last question
    # so we can see what happens when we use `start` and we're already done
    with patch("hacenada.session.Session.step_session", side_effect=error.ScriptFinished):
        invoked = runner.invoke(main.start, ["--start-over", "project.toml"])
    assert invoked.exit_code == 0, f"{invoked.exit_code} {invoked.exception}"
    assert "project.toml: Cleaning up.  Log: " in invoked.stdout


def test_next(runner: CliRunner, my_project: pathlib.Path, storagie):
    """
    Do we handle all the states of starting and starting over?
    """
    p_render = patch(
        "hacenada.render.PyInquirerRender.render",
        autospec=True,
        return_value={"message-1": "yes"},
    )

    # start with 1 storage
    storagie.save_answer({"q1": "descriptiono"})
    with p_render:
        invoked = runner.invoke(main.next)
    assert storagie.get_answer("message-1")["value"] == "yes"
    assert invoked.exit_code == 0, f"{invoked.exit_code} {invoked.exception}"
    assert "project.toml: Cleaning up.  Log: " in invoked.stdout

    # this invocation fails, storage file has disappeared
    for found in my_project.parent.parent.glob("*.json"):
        found.unlink()
    invoked = runner.invoke(main.next)
    assert "No possible storage" in invoked.stdout
    assert invoked.exit_code > 0
