# Hacenada

Write do-nothing scripts in a declarative (ini) syntax


## Installation
```
pip install hacenada
```

## Usage

```#!bash
hacenada start example/release.toml
... interact with the first step

hacenada next
... interact with the second step
```

### Quick syntax reference

You must include a `[hacenada]` section at the top, with `name` and optional `description`.

Then create as many `[[step]]` sections as you want.

The minimum for a step is a single `message = "the message"` entry under each `[[step]]`.

#### **Example**

(Save this as `install-hacenada.toml`.)

```
[hacenada]
name = "Install hacenada"
description = """
This will walk you through the installation of Hacenada. Installing hacenada is fun to do!
"""

[[step]]
message = """
First, use pip to install hacenada from pypi.

`pip install hacenada`
"""


[[step]]
message = "that was it, you're done"
```

Then run it:

```#!bash
hacenada start install-hacenada.toml
```

You will be shown the first step. To continue:

```#!bash
hacenada next
```

You will be shown the second step.

After the second step, since there are no more steps, Hacenada saves a log of
the whole session to `install-hacenada.log.d/`.

## Command reference

- `hacenada start <filename.toml>`

  Start running a Hacenada script. Hacenada checks
  to see if you have previously started running this
  script. If so, you will see an error.

  You may add `--start-over` to restart the script fresh.

- `hacenada next [optional filename.toml]`

  Continue running a script at the next step.

  The filename is usually optional here. (If the
  directory contains multiple scripts and you
  have previously started more than one of them,
  you will see an error and you should specify which
  script you meant.)

- `hacenada print [--format=...] [optional filename.toml]`

  Print the script and optionally the answers to each step, in one of three formats: `json`, `toml` (the default), or `markdown`. If any steps have been answered, `hacenada print` will include those answers by default.

  The filename is optional and works the same way as with `hacenada next`.



## Syntax reference

### Top level sections

- `[hacenada]`
  - `name =`

    The name of the script, which will be shown at each step.

  - `description =`

    A longer description of the script.


- `[step]` or `[[step]]`

  (_NOTE:_ You will almost always see the second form, with two brackets, for
  readability's sake.)

  The list of steps that will be shown one after the other.

  The two bracket `[[step]]` form is TOML syntax; the contents of the
  `[step]` section is actually a list. In TOML, `[[step]]` just adds one item
  to that list. Just follow the examples, and use `[[step]]` if this seems
  confusing.


### Properties of `[[step]]`

- `message =`

  The text that will be displayed for the step. You may make this multiline
  by using TOML `"""` syntax, see examples.

- `type =` _(optional; default "message")_

  The step question type. Valid types are:

  * `message`: displays the message, with a confirmation prompt. `confirm`
    is an alias for the same type, and may be used interchangeably.
  * `input`: ask the user to type in some free text
  * `description`: asks for the user to type in a description. This is saved
    like `input`, but the description is also displayed before each step (after
    this one), and also used as part of the log file name.
  * **TODO**: `editor`, `choice`, `run`, `password`, others.

  It is recommended that you include a `type="description"` step somewhere
  near the beginning.

- `label =` _(optional; default is autogenerated)_

  Assign a label id to this step. If not specified, the step is given a label
  which includes the type and the step number, for example, `message-11`.

- `stop =` _(optional; default `true`)_

  Whether to stop the script after this step. By default, hacenada shows one
  step and then stop. You are expected to run `hacenada next` to see the next
  step.

  If you set `stop = false` on a step, hacenada will show the next step without
  exiting.

## Roadmap

- Steps:
  - Add support for running bash (or python?) code, with answer=stdout/stderr
  - Add support for input via choice inputs, text editor inputs

- Rendering options:
  - ipynb rendering support
  - Display markdown more prettily in a text terminal

- Backend options:
  - cloud service for storage backend


## Change Log

### [0.1.2] - 2021.01.14
  - First numbered release.
  - Current features:
    - Parse a toml script (only type=description and type=message for now)
    - Display questions and save answers in a tinydb
    - Recover state between runs, or start over
    - After the last step, write a log with what happened
    - Markdown, TOML and JSON print output of the script+answers
    - Python 3.7, 3.8, 3.9 support

[0.1.2]: https://github.com/corydodt/Codado/tree/v0.1.2
