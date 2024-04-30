from datetime import datetime
from typing import Optional

from sqlmodel import Column, DateTime, Field, SQLModel, func


class SysMenu(SQLModel, table=True):
    __tablename__ = 'sys_menu'
    id: Optional[int] = Field(default=None, primary_key=True, description="主键")
    status: int = Field(default=1, description="状态 1有效 9 删除 5选中")
    created: datetime = Field(nullable=True,
                              description="创建时间",
                              default_factory=datetime.utcnow)
    modified: datetime = Field(default=None,
                               description="更新时间",
                               sa_column=Column(DateTime(),
                                                onupdate=func.now()))
    name: Optional[str] = Field(default=None,
                                max_length=20,
                                nullable=True,
                                description="名称")
    icon: Optional[str] = Field(default=None,
                                max_length=100,
                                nullable=True,
                                description="菜单图标")
    path: Optional[str] = Field(default=None,
                                max_length=128,
                                nullable=True,
                                description="菜单url")
    type: int = Field(default=...,
                      description="菜单类型 0目录 1组件 2按钮 3数据",
                      index=True)
    component: Optional[str] = Field(default=None,
                                     max_length=128,
                                     nullable=True,
                                     description="组件地址")
    pid: Optional[int] = Field(default=None, nullable=True, description="父id")
    identifier: Optional[str] = Field(default=None,
                                      max_length=30,
                                      nullable=True,
                                      description="权限标识 user:add")
    api: Optional[str] = Field(default=None,
                               max_length=128,
                               nullable=True,
                               description="接口地址")
    method: Optional[str] = Field(default=None,
                                  max_length=10,
                                  nullable=True,
                                  description="接口请求方式")