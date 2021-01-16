"""
Test the rendering mechanism to see if inquirer works
"""
from unittest.mock import Mock, create_autospec, patch

import inquirer
from pytest import fixture

from hacenada import render, session


@fixture
def renderer():
    rr = render.InquirerRender()
    return rr


def test_inquirer_type(renderer):
    """
    Do I look up inquirer question type by hacenada typename?
    """
    assert renderer._inquirer_dispatch("description") is inquirer.text


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
    prompt = Mock(return_value="here we go")
    with patch.object(
        render.InquirerRender, "_inquirer_dispatch", autospec=True, return_value=prompt
    ) as m_prompt:
        ret = renderer.render(steppie, seshie)

    m_prompt.return_value.assert_called_once_with("DESCRIPTION : q1\noh noo\n>>")
    assert ret == {"q1": "here we go"}


def test_render_no_description(renderer, steppie, seshie):
    """
    Do I display the right title when there's no description property set?
    """
    seshie.storage.description = None
    seshie.script.preamble = {"name": "SCRIPT NAME"}
    prompt = Mock(return_value="here we go")
    with patch.object(
        render.InquirerRender, "_inquirer_dispatch", autospec=True, return_value=prompt
    ) as m_prompt:
        renderer.render(steppie, seshie)

    m_prompt.return_value.assert_called_once_with("SCRIPT NAME : q1\noh noo\n>>")
