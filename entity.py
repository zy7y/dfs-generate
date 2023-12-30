import uuid
from typing import Generic, List, Optional, TypeVar

import black
import isort
from pydantic import BaseModel, ConfigDict, field_serializer
from pydantic.alias_generators import to_camel
from sqlmodel import Field, MetaData, Session, SQLModel, create_engine, select

db_uri = "sqlite:///main.sqlite"
engine = create_engine(db_uri)


def get_metadata_by_db_uri(uri: str):
    db_engine = create_engine(uri)
    db_metadata = MetaData()
    db_metadata.reflect(bind=db_engine)
    return db_metadata


class Conf(SQLModel, table=True):
    __tablename__ = "dfs_conf"
    id: int = Field(None, primary_key=True)
    db_uri: str = Field(..., description="数据库连接")

    @classmethod
    def get_db_uri_last_new(cls):
        """获取最新的db_url"""
        with Session(engine) as session:
            query = select(cls).order_by(cls.id.desc())
            latest_conf = session.exec(query).first()
            if latest_conf:
                return latest_conf.db_uri
            else:
                return None

    @classmethod
    def create(cls, uri) -> "Conf":
        with Session(engine) as session:
            obj = cls(db_uri=uri)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj

    @classmethod
    def get_last_uri_with_metadata(cls):
        uri = cls.get_db_uri_last_new()
        return uri, get_metadata_by_db_uri(uri)


T = TypeVar("T")


class R(BaseModel, Generic[T]):
    code: int = 20000
    msg: str = "ok"
    data: Optional[T] = None

    @classmethod
    def success(cls, **kwargs):
        return cls(**kwargs)

    @classmethod
    def error(cls, msg):
        return cls(code=40000, msg=msg)


class RList(R[T]):
    data: List[T] = Field(default_factory=list)


class BaseVo(SQLModel):
    key: uuid.UUID = Field(default_factory=uuid.uuid4)
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class Table(BaseVo):
    table_name: str
    table_comment: Optional[str] = None


class DBConf(SQLModel):
    user: str
    password: str
    port: int
    host: str
    db: str

    def get_db_uri(self):
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    def get_metadata(self):
        return get_metadata_by_db_uri(self.get_db_uri())


class CodeGen(BaseVo):
    name: str
    code: str

    @field_serializer("code")
    def serialize_code(self, code: str, _info):
        _code = black.format_str(code, mode=black.FileMode())
        return isort.code(_code)
