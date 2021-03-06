"""
Exception classes for hacenada
"""


class StorageError(Exception):
    """
    Base class for all storage-related errors
    """


class MultipleNextFound(StorageError):
    """
    More than one possible session exists in this directory, can't automatically pick one
    """


class NoNextFound(StorageError):
    """
    No pre-existing session found for this directory
    """


class ScriptFinished(Exception):
    """
    Signal that the interpreter reached the end of the script
    """


class RenderError(Exception):
    """
    Base for all rendering-related errors
    """
