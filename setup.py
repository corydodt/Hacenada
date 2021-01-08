from setuptools import find_packages, setup


VERSION = "0.0.1+dev"


data = {
    "name": "Hacenada",
    "version": VERSION,
    "description": "Write do-nothing scripts",
    "packages": find_packages(where="./src", include=("hacenada", "hacenada.*")),
    "package_dir": {"": "src"},
    "install_requires": [
        "attrs",
        "click",
        "codado",
        "pyinquirer",
        "toml",
    ],
    "extras_require": {
        "dev": [
            "isort",
            "mypy",
            "pytest",
            "pytest-coverage",
            "pytest-flake8",
            "tox",
            "black",
        ]
    },
    "scripts": ["bin/hacenada"],
}

setup(**data)
