"""
Common fixtures
"""
import os
from pathlib import Path
import shutil
from unittest.mock import patch

from pytest import fixture


MY_TOML = """
[hacenada]
name = "hola"
description = "nice little script ya got here"

[[step]]
type = "description"
message = "oh noo"
label = "q1"
stop = true

[[step]]
message = "shame if something were to happen to it"
"""


@fixture
def my_project(tmpdir):
    """
    A project .toml we can use
    - also changes directories to this project
    - and sets the tmpdir parent as HACENADA_HOME
    """
    cwd = os.getcwd()
    hacenada_home = Path(tmpdir)
    (hacenada_home / "project").mkdir()
    toml = hacenada_home / "project/project.toml"
    toml.write_text(MY_TOML)
    try:
        os.chdir(hacenada_home / "project")
        with patch("hacenada.storage.HACENADA_HOME", hacenada_home):
            yield toml
    finally:
        os.chdir(cwd)

    shutil.rmtree(hacenada_home)


@fixture
def scriptie(my_project):
    """
    A fully-realized script object
    """
    from hacenada import script

    return script.Script.from_scriptfile(my_project)


@fixture
def steppie():
    """
    A useful script step
    """
    return dict(
        type="description",
        message="oh noo",
        label="q1",
        stop=True,
    )


@fixture
def storagie(my_project: Path):
    """
    A storage instance created from our project
    """
    from hacenada import storage

    ret = storage.HomeDirectoryStorage.from_path(my_project)

    assert ret.script_path == my_project
    normaled = storage._normalize_path(my_project, ".json")
    assert (storage.HACENADA_HOME / f"{normaled}").exists()

    yield ret
