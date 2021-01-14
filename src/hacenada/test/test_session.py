"""
Do we manage a session properly?
"""
from unittest.mock import ANY, MagicMock, call, create_autospec

from pytest import fixture, raises

from hacenada import abstract, error, session


@fixture
def storagie():
    """
    A mock storage
    """
    ret = create_autospec(abstract.SessionStorage)
    ret.answer = []
    ret.meta = {}
    return ret


@fixture
def sesho(storagie, scriptie):
    opts = session.SessionOptions(renderer=MagicMock())
    return session.Session(
        storage=storagie,
        script=scriptie,
        options=opts,
    )


def test_started(sesho):
    """
    Do we use the appropriate criteria to determine whether a session is in-progress?
    """
    assert not sesho.started
    sesho.storage.answer = [1, 2]
    assert sesho.started


def test_step_session(sesho):
    """
    Do we correctly navigate a session with multiple questions?
    """
    sesho.storage.answer = ["skipping_first_question"]
    sesho.options.renderer.render.return_value = {"message-1": "True"}
    with raises(error.ScriptFinished):
        sesho.step_session()

    # were we shown the second question first?
    assert sesho.options.renderer.render.call_args_list[0] == call(
        {"label": "message-1", "message": ANY, "stop": ANY, "type": "message"},
        context=sesho,
    )

    # also make sure meta description gets set after a description question
    sesho.storage.answer = []
    sesho.options.renderer.render.return_value = {"q1": "description19"}
    sesho.step_session()
    assert sesho.storage.description == "description19"


def test_step_session_unanswered(sesho, capsys):
    """
    Do we abort on Unanswered?
    """
    sesho.options.renderer.render.side_effect = error.Unanswered("oh no")
    sesho.step_session()
    assert capsys.readouterr()[0] == "** Canceled at q1\n"
