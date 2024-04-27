from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel

T = TypeVar("T")


class Result(BaseModel, Generic[T]):
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="额外消息")
    data: Optional[T] = Field(None, description="响应数据")

    @classmethod
    def ok(cls, data: T, message: str = "成功"):
        return cls(data=data, message=message, success=True)

    @classmethod
    def error(cls, message: str = "失败"):
        return cls(data=None, message=message, success=False)


class PageResult(Result[T]):
    total: int = Field(0, description="数据总数")
    data: List[T] = Field(default_factory=list, description="响应数据")

    @classmethod
    def ok(cls, data: List[T], message: str = "成功", total: int = 0):
        return cls(data=data, total=total, message=message, success=True)


class Aerich(BaseModel):
    id: Optional[int] = None
    version: Optional[str] = None
    app: Optional[str] = None
    content: Optional[dict] = None
    model_config = {"alias_generator": to_camel, "populate_by_name": True}
