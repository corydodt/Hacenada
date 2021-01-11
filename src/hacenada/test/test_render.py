"""
Test the rendering mechanism to see if pyinquirer works
"""
from unittest.mock import ANY, create_autospec, patch

from pytest import fixture, raises

from hacenada import error, render, session


@fixture
def renderer():
    rr = render.PyInquirerRender()
    return rr


def test_inquirer_type(renderer):
    """
    Do I look up pyinquirer question type by hacenada typename?
    """
    assert renderer._inquirer_type("description") == "input"


@fixture
def seshie():
    """
    A mock session
    """
    sesh = create_autospec(session.Session)
    sesh.storage.description = "DESCRIPTION"
    return sesh


def test_render(renderer, steppie, seshie):
    """
    Do I render questions to the screen?
    """
    with patch.object(
        render.pyinquirer, "prompt", autospec=True, return_value={"q1": "here we go"}
    ) as m_prompt:
        ret = renderer.render(steppie, seshie)

    m_prompt.assert_called_once_with(
        questions=[
            {"name": "q1", "message": "DESCRIPTION : q1\noh noo\n>>", "type": "input"}
        ],
        answers={},
    )
    assert ret == {"q1": "here we go"}


def test_render_canceled(renderer, steppie, seshie):
    """
    Do I raise when no answer was given?
    """
    with patch.object(render.pyinquirer, "prompt", autospec=True, return_value={}):
        with raises(error.Unanswered):
            renderer.render(steppie, seshie)


def test_render_no_description(renderer, steppie, seshie):
    """
    Do I display the right title when there's no description property set?
    """
    seshie.storage.description = None
    seshie.script.preamble = {"name": "SCRIPT NAME"}
    with patch.object(
        render.pyinquirer, "prompt", autospec=True, return_value={"q1": "here we go"}
    ) as m_prompt:
        renderer.render(steppie, seshie)

    m_prompt.assert_called_once_with(
        questions=[
            {
                "name": ANY,
                "message": "SCRIPT NAME : q1\noh noo\n>>",
                "type": ANY,
            }
        ],
        answers=ANY,
    )
