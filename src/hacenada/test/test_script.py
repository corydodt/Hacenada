"""
Do we turn a toml scriptfile into a displayable script?
"""

from hacenada import script


def test_autolabel(steppie):
    """
    Do I produce a good label for a particular step+type?
    """
    assert script.Script.autolabel(steppie, 19) == "description-19"


def test_preprocess(scriptie):
    """
    Do we fix the gaps in the script steps?
    """
    fixed_step = scriptie.overlay[1]
    assert fixed_step["stop"] is True
    assert fixed_step["type"] == "message"
    assert fixed_step["label"] == "message-1"
