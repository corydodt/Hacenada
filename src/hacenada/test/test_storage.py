"""
Tests that we can interact with storage
"""
from pathlib import Path
from unittest.mock import ANY

from pytest import mark, raises

from hacenada import error, storage


@mark.parametrize(
    "input,suffix,output",
    [
        ["hellO", None, "hellO"],
        ["/is/it/me/youre/looking/for/", None, "is__it__me__youre__looking__for"],
        [
            "/i/can/see/it/in/your/smile.toml",
            ".json",
            "i__can__see__it__in__your__smile.json",
        ],
    ],
)
def test_normalize_path(input, suffix, output):
    """
    Do I turn strings into other strings that can be filenames?
    """
    input = Path(input)
    assert storage._normalize_path(input, suffix) == output


def test_from_cwd(my_project):
    """
    Given a cwd, do we correctly find the storage
    """
    # 1. no storage exists, check the exception
    with raises(error.NoNextFound):
        _ = storage.HomeDirectoryStorage.from_cwd()

    # 2. create the storage, ensure we succeed at creation
    storage.HomeDirectoryStorage.from_path(my_project)

    stor = storage.HomeDirectoryStorage.from_cwd()
    assert stor.script_path == my_project
    normaled = storage._normalize_path(my_project, ".json")
    assert (storage.HACENADA_HOME / f"{normaled}").exists()

    # 3. create another storage, check the exception
    normaled2 = Path(normaled).stem + "2.json"
    (storage.HACENADA_HOME / f"{normaled2}").touch()
    with raises(error.MultipleNextFound):
        _ = storage.HomeDirectoryStorage.from_cwd()


def test_save_get_answer(storagie):
    """
    Can I save and retrieve an answer from storage?
    """
    storagie.save_answer({"q1": "a1"})
    assert len(storagie.answer) == 1
    assert storagie.get_answer("q1") == storage.Answer(label="q1", value="a1", when=ANY)


def test_save_get_meta(storagie):
    """
    Can I save and retrieve properties from meta?
    """
    assert not storagie.description
    storagie.description = "hello there"
    assert storagie.description == "hello there"

    storagie.script_path = Path("oh/no")
    assert storagie.script_path == Path("oh/no")


def test_to_structured(storagie):
    storagie.save_answer({"q1": "a1"})
    storagie.save_answer({"q2": "a 2"})
    storagie.description = "hello there"

    assert storagie.to_structured() == dict(
        answer=[
            storage.Answer(label="q1", value="a1", when=ANY),
            storage.Answer(label="q2", value="a 2", when=ANY),
        ],
        meta=dict(
            description="hello there",
            script_path=str(storagie.script_path),
        ),
    )


def test_drop_path(my_project, storagie):
    """
    Do we clear the data that goes with this project toml file?
    """
    assert Path(storagie.script_path) == my_project
    storagie.save_answer({"q1": "a1"})
    storagie.save_answer({"q2": "a 2"})
    storagie.description = "hello there"

    assert len(storagie.answer) == 2
    assert storagie.description

    storage.HomeDirectoryStorage.drop_path(my_project)
    store2 = storage.HomeDirectoryStorage.from_path(my_project)

    assert len(store2.answer) == 0
    assert not store2.description
