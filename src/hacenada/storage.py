"""
Built-in storage abstractions
"""
from __future__ import annotations

import datetime
import pathlib
import typing

import attr
from tinydb import TinyDB, table, where
from tinydb_serialization import SerializationMiddleware, Serializer

from hacenada import compat, error
from hacenada.abstract import SessionStorage
from hacenada.const import STR_DICT


ENCODING = "utf-8"
HACENADA_HOME = pathlib.Path.home() / ".hacenada"


class Answer(compat.TypedDict):
    label: str
    value: typing.Any
    when: datetime.datetime


def _normalize_path(pth: pathlib.Path, suffix: typing.Optional[str] = None) -> str:
    """
    Produce a string version of pth replacing / with __ to produce a legal filename

    Replace suffix at the end if specified
    """
    if suffix is not None:
        pth = pth.with_suffix(suffix)

    s = str(pth)
    return s.strip("/").replace("/", "__")


@attr.s(auto_attribs=True)
class HomeDirectoryStorage(SessionStorage):
    """
    Access to session storage through a tinydb in a known location in $HOME
    """

    db: TinyDB
    answer: table.Table
    meta: table.Table

    def to_structured(self):
        return dict(meta=self.meta.all()[0], answer=self.answer.all())

    @classmethod
    def from_path(cls, path: pathlib.Path) -> HomeDirectoryStorage:
        """
        From the path to the .toml script, find the storage in the homedir
        """
        normal = _normalize_path(path.absolute(), suffix=".json")
        self = cls._from_json_path(HACENADA_HOME / normal)
        self.script_path = path
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
        if len(any_json) > 1:
            raise error.MultipleNextFound(
                f"Multiple possible storages found: {[str(p) for p in any_json]}"
            )
        elif len(any_json) <= 0:
            raise error.NoNextFound(f"No possible storage found corresponding to {cwd}")

        return cls._from_json_path(any_json[0])

    @classmethod
    def _from_json_path(cls, path: pathlib.Path) -> HomeDirectoryStorage:
        """
        SessionStorage from a Path to a .json tinydb
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        db = _new_db(path)
        answer = db.table("answer")
        meta = db.table("meta")
        if len(meta) == 0:
            meta.insert({})
        return cls(db=db, answer=answer, meta=meta)

    def save_answer(self, answer: STR_DICT):
        """
        Save one answer to tinydb
        """
        k, v = list(answer.items())[0]
        d = Answer(label=k, value=v, when=datetime.datetime.now())
        self.answer.upsert(d, where("label") == list(answer.keys())[0])

    def update_meta(self, **kw):
        """
        Save any property k=v pair to the meta properties
        """
        props = self.meta.all()[0]
        props.update(kw)
        self.meta.update(props)

    def get_answer(self, label: str) -> typing.Optional[Answer]:
        """
        Look up an answer by label string in tinydb
        """
        ans = self.answer.get(where("label") == label)
        if ans is None:
            return None

        return Answer(label=ans["label"], value=ans["value"], when=ans["when"])

    @classmethod
    def drop_path(cls, toml_path):
        """
        Drop the storage corresponding to toml_path, which is a .toml filename
        """
        store = cls.from_path(toml_path)
        store.answer.truncate()
        store.meta.truncate()
        store.meta.insert({})

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
    def script_path(self) -> pathlib.Path:
        """
        The meta script_path of the session
        """
        return pathlib.Path(self.meta.all()[0].get("script_path", ""))

    @script_path.setter
    def script_path(self, value: pathlib.Path):
        """
        Set the meta script_path of the session in tinydb
        """
        self.update_meta(script_path=str(value))


class DateTimeSerializer(Serializer):
    """
    Round trip datetimes (which are also timezone-aware) through tinydb
    """
    OBJ_CLASS = datetime.datetime

    def encode(self, obj: datetime.datetime) -> str:
        if obj.tzinfo is None:
            # naive == local timezone. insert utc timezone and adjust
            obj = obj.astimezone(datetime.timezone.utc)
        return obj.isoformat()

    def decode(self, s: str) -> datetime.datetime:
        ret = datetime.datetime.fromisoformat(s)
        assert ret.tzinfo is not None
        return ret


def _new_db(path: pathlib.Path) -> TinyDB:
    """
    Construct a TinyDB with our customizations
    """
    serialization = SerializationMiddleware()
    serialization.register_serializer(DateTimeSerializer(), 'TinyDate')
    return TinyDB(path, storage=serialization)
