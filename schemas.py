import uuid
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

DataT = TypeVar("DataT")


class RMixin(BaseModel):
    code: int = 20000
    msg: str = "ok"


class R(RMixin, Generic[DataT]):
    data: DataT = None

    @classmethod
    def success(cls, **kwargs) -> "R":
        return cls(**kwargs)

    @classmethod
    def error(cls, msg) -> "R":
        return cls(code=40000, msg=msg)


class BaseVO(BaseModel):
    key: uuid.UUID = Field(default_factory=uuid.uuid4)
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class TableVO(BaseVO):
    table_name: str = Field(..., title="表名")
    table_comment: Optional[str] = Field(None, title="表描述")


class ChangeDB(BaseModel):
    user: str
    password: str
    port: int
    host: str
    db: str


class CodeGen(BaseVO):
    key: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    code: str
