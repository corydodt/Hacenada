from setuptools import find_packages, setup


VERSION = "0.1.2"


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

data = {
    "name": "Hacenada",
    "classifiers": [
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    "description": "Write do-nothing scripts",
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
    "install_requires": [
        "attrs",
        "click",
        "codado",
        "tinydb-serialization",
        "typing_extensions; python_version < '3.8'",
        "pyinquirer",
        "tinydb",
        "toml",
    ],
    "long_description": long_description,
    "long_description_content_type": "text/markdown",
    "packages": find_packages(where="./src", include=("hacenada", "hacenada.*")),
    "package_dir": {"": "src"},
    "scripts": ["bin/hacenada"],
    "url": "https://github.com/corydodt/Hacenada",
    "version": VERSION,
}

setup(**data)
