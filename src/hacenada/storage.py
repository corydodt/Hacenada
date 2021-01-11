"""
Built-in storage abstractions
"""
from __future__ import annotations

import pathlib
import typing

import attr
import tinydb

from hacenada.const import STR_DICT
from hacenada.abstract import SessionStorage


ENCODING = "utf-8"
HACENADA_HOME = pathlib.Path.home() / ".hacenada"


def _normalize_path(pth: pathlib.Path, suffix: typing.Optional[str] = None) -> str:
    """
    Produce a string version of pth replacing / with __ to produce a legal filename

    Replace suffix at the end if specified
    """
    if suffix is not None:
        pth = pth.with_suffix(suffix)

    s = str(pth)
    return s.lstrip("/").replace("/", "__")


@attr.s(auto_attribs=True)
class HomeDirectoryStorage(SessionStorage):
    """
    Access to session storage through a tinydb in a known location in $HOME
    """

    db: tinydb.TinyDB
    answer: tinydb.table.Table
    meta: tinydb.table.Table

    def to_structured(self):
        return dict(meta=self.meta.all()[0], answer=self.answer.all())

    @classmethod
    def from_path(cls, path: pathlib.Path) -> HomeDirectoryStorage:
        """
        From the path to the .toml script, find the storage in the homedir
        """
        normal = _normalize_path(path.absolute(), suffix=".json")
        self = cls._from_json_path(HACENADA_HOME / normal)
        self.script_path = str(path)
        return self

    #  @classmethod
    #  def from_id(cls, id: str) -> HomeDirectoryStorage:
    #      normal = id + ".json"
    #      return cls._from_json_path(HACENADA_HOME / normal)

    @classmethod
    def from_cwd(cls) -> HomeDirectoryStorage:
        """
        Try to infer the session storage from the directory we're currently in.

        Looks for any storage.json that has a prefix of the current absolute cwd path.
        """
        cwd = pathlib.Path.cwd()
        normal = _normalize_path(cwd, "")
        any_json = list(HACENADA_HOME.glob(f"{normal}*.json"))
        assert len(any_json) < 2, f"Multiple possible storages found: {any_json}"
        assert len(any_json) == 1, f"No possible storage found corresponding to {cwd}"
        return cls._from_json_path(any_json[0])

    @classmethod
    def _from_json_path(cls, path: pathlib.Path) -> HomeDirectoryStorage:
        """
        SessionStorage from a Path to a .json tinydb
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        db = tinydb.TinyDB(path)
        answer = db.table("answer")
        meta = db.table("meta")
        if len(meta) == 0:
            meta.insert({})
        return cls(db=db, answer=answer, meta=meta)

    def save_answer(self, answer: STR_DICT):
        """
        Save one answer to tinydb
        """
        Answer = tinydb.Query()
        d = {}
        for k, v in answer.items():
            d["label"] = k
            d["value"] = v
        self.answer.upsert(d, Answer.label == list(answer.keys())[0])

    def update_meta(self, **kw):
        """
        Save any property k=v pair to the meta properties
        """
        props = self.meta.all()[0]
        props.update(kw)
        self.meta.update(props)

    def get_answer(self, label: str):
        """
        Look up an answer by label string in tinydb
        """
        Answer = tinydb.Query()
        return self.answer.get(Answer.label == label)

    def drop(self):
        """
        Drop all items in the tinydb
        """
        self.db.truncate()
        self.answer.truncate()
        self.meta.truncate()
        self.meta.insert({})

    @property
    def description(self) -> str:
        """
        The meta description of the session
        """
        return self.meta.all()[0].get("description", "")

    @description.setter
    def description(self, value: str):
        """
        Set the meta description of the session in tinydb
        """
        self.update_meta(description=value)

    @property
    def script_path(self) -> str:
        """
        The meta script_path of the session
        """
        return self.meta.all()[0]["script_path"]

    @script_path.setter
    def script_path(self, value: str):
        """
        Set the meta script_path of the session in tinydb
        """
        self.update_meta(script_path=value)
