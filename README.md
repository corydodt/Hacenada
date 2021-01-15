# Hacenada

Write do-nothing scripts in a declarative (ini) syntax


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
