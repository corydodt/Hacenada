from setuptools import setup, find_packages


VERSION = '0.0.1+dev'


data = {
    'name': 'Hacenada',
    'version': VERSION,
    'description': 'Write do-nothing scripts',
    'packages': find_packages(where='src', include=('hacenada', 'hacenada.*')),

    'install_requires': [
        'click',
        'codado',
        'inquirer',
    ],
    'extras_require': [
        'pytest',
        'tox',
        'flake8',
        'black',
    ]
}

setup(**data)
