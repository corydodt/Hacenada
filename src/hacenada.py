"""
Write do-nothing scripts, inspired by https://blog.danslimmon.com/2019/07/15/do-nothing-scripting-the-key-to-gradual-automation/

(From the Spanish, "hace nada" meaning "it does nothing")
"""

import click
import inquirer
from codado import hotedit


@click.command()
def hacenada():
    """
    1. Load a template from .hacenada.tpl
    2. prompt for a description
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
    - --startover will let you discard a run in process. this writes the (incomplete) log to the logs dir as
        if you had finished.
    - use codado.hotedit for interactive editor steps

    - challenges: it needs to be easy/lightweight for an operator to run a script. The script already
      imports several third-party libraries and I haven't even written any code yet.
      minimize dependencies or have a canonical way (like a curl-pipe-bash installer?)

      could also be a snap install!
    """
    inquirer.prompt()
    hotedit.hotedit()
