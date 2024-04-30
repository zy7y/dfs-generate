from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel

T = TypeVar('T')


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


class PageParam(BaseModel):
    page_number: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页数量")

    model_config = {"alias_generator": to_camel, "populate_by_name": True}


class SysMenu(BaseModel):
    id: Optional[int] = Field(None, description='主键')
    status: Optional[int] = Field(None, description='状态 1有效 9 删除 5选中')
    created: Optional[datetime] = Field(None, description='创建时间')
    modified: Optional[datetime] = Field(None, description='更新时间')
    name: Optional[str] = Field(None, description='名称')
    icon: Optional[str] = Field(None, description='菜单图标')
    path: Optional[str] = Field(None, description='菜单url')
    type: Optional[int] = Field(None, description='菜单类型 0目录 1组件 2按钮 3数据')
    component: Optional[str] = Field(None, description='组件地址')
    pid: Optional[int] = Field(None, description='父id')
    identifier: Optional[str] = Field(None, description='权限标识 user:add')
    api: Optional[str] = Field(None, description='接口地址')
    method: Optional[str] = Field(None, description='接口请求方式')
    model_config = {"alias_generator": to_camel, "populate_by_name": True}
