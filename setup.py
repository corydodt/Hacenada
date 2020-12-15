from setuptools import find_packages, setup

VERSION = "0.0.1+dev"


data = {
    "name": "Hacenada",
    "version": VERSION,
    "description": "Write do-nothing scripts",
    "packages": find_packages(where="src", include=("hacenada", "hacenada.*")),
    "install_requires": [
        "click",
        "codado",
        "inquirer",
    ],
    "extras_require": {
        "dev": [
            "isort",
            "pytest",
            "pytest-coverage",
            "pytest-flake8",
            "tox",
            "black",
        ]
    },
}

setup(**data)
