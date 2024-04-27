RESPONSE_SCHEMA = """
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel
T = TypeVar('T')
class Result(BaseModel, Generic[T]):
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="额外消息")
    data: Optional[T] = Field(None, description="响应数据")

    @classmethod
    def ok(cls, data: T, message: str="成功"):
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
"""

SQLMODEL_DAO = """
def create(session: Session, obj_in: schema.{table}) -> model.{table}:
    obj = model.{table}(**obj_in.dict())
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj

def query_by_id(session: Session, id: int) -> Optional[model.{table}]:
    return session.get(model.{table}, id)

def update(session: Session, id: int, obj_in: schema.{table}) -> Optional[model.{table}]:
    obj = query_by_id(session, id)
    if obj:
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(obj, field, value)
        session.add(obj)
        session.commit()
        session.refresh(obj)
    return obj

def delete_by_id(session: Session, id: int) -> Optional[model.{table}]:
    obj = session.get(model.{table}, id)
    if obj:
        session.delete(obj)
        session.commit()
    return obj

def count(session: Session, **kwargs) -> int:
    return session.scalar(
select(func.count()).
select_from(model.{table}).filter_by(**kwargs)
)

def query_all_by_limit(session: Session, page_number: int, page_size: int, **kwargs) -> List[model.{table}]:
    stmt = select(model.{table}).filter_by(**kwargs).offset((page_number - 1) * page_size).limit(page_size)
    return session.exec(stmt).all()
"""

SQLMODEL_ROUTER = """
from fastapi import APIRouter, Depends
from sqlmodel import Session
import schema
import dao
from db import engine

$router_name = APIRouter(prefix="/$table", tags=["$table"])

@$router_name.get("/{id}", summary="通过ID查询详情")
def query_${router_name}_by_id(id: int) -> schema.Result[schema.$table]:
    with Session(engine) as session:
        return schema.Result.ok(dao.query_by_id(session, id))

@$router_name.get("", summary="分页条件查询")
def query_${router_name}_all_by_limit(query: schema.$table = Depends(), page_number: int = 1, page_size: int = 10) -> schema.PageResult[schema.$table]:
    with Session(engine) as session:
        total = dao.count(session, **query.model_dump(exclude_none=True))
        data = dao.query_all_by_limit(session, **query.model_dump(exclude_none=True), page_number=page_number, page_size=page_size)
        return schema.PageResult.ok(data=data, total=total)


@$router_name.post("", summary="新增数据")
def create_${router_name}(instance: schema.$table) -> schema.Result[schema.$table]:
    with Session(engine) as session:
        return schema.Result.ok(dao.create(session, instance))


@$router_name.patch("/{id}", summary="更新数据")
def update_${router_name}_by_id(id: int, instance: schema.$table) -> schema.Result[schema.$table]:
    with Session(engine) as session:
        return schema.Result.ok(dao.update(session, id, instance))


@$router_name.delete("/{id}", summary="删除数据")
def delete_${router_name}_by_id(id: int) -> schema.Result[schema.$table]:
    with Session(engine) as session:
        return schema.Result.ok(dao.delete_by_id(session, id))
"""

SQLMODEL_DB = """
from sqlmodel import create_engine

db_uri = "{uri}"

engine = create_engine(db_uri)
"""

SQLMODEL_MAIN = """
from fastapi import FastAPI

from router import {router_name}


app = FastAPI(title="DFS - FastAPI SQLModel CRUD", 
description='''
[![](https://img.shields.io/github/stars/zy7y/dfs-generate)](https://github.com/zy7y/dfs-generate)
[![](https://img.shields.io/github/forks/zy7y/dfs-generate)](https://github.com/zy7y/dfs-generate)
[![](https://img.shields.io/github/repo-size/zy7y/dfs-generate?style=social)](https://github.com/zy7y/dfs-generate)
[![](https://img.shields.io/github/license/zy7y/dfs-generate)](https://gitee.com/zy7y/dfs-generate/blob/master/LICENSE)

支持ORM：[SQLModel](https://sqlmodel.tiangolo.com/)、[Tortoise ORM](https://tortoise.github.io/)

支持前端: [Vue](https://cn.vuejs.org/)、[React](https://zh-hans.react.dev/)'''

)


app.include_router({router_name})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", reload=True, port=5000)
"""

TORTOISE_DAO = """
async def create(obj_in: schema.{table}) -> model.{table}:
    obj = model.{table}(**obj_in.dict())
    await obj.save()
    return obj

async def query_by_id(id: int) -> Optional[model.{table}]:
    return await model.{table}.get_or_none(id=id)

async def update(id: int, obj_in: schema.{table}) -> Optional[model.{table}]:
    obj= await query_by_id(id)
    if obj:
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(obj, field, value)
        await obj.save()
    return obj

async def delete_by_id(id: int) -> Optional[model.{table}]:
    obj = await query_by_id(id)
    if obj:
        await obj.delete()
    return obj

async def count(**kwargs) -> int:
    return await model.{table}.filter(**kwargs).count()

async def query_all_by_limit(page_number: int, page_size: int, **kwargs) -> List[model.{table}]:
    offset = (page_number - 1) * page_size
    limit = page_size
    return await model.{table}.filter(**kwargs).offset(offset).limit(limit).all()
"""

TORTOISE_ROUTER = """
from fastapi import APIRouter, Depends
import schema
import dao

$router_name = APIRouter(prefix="/$table", tags=["$table"])

@$router_name.get("/{id}", summary="通过ID查询详情")
async def query_${router_name}_by_id(id: int) -> schema.Result[schema.$table]:
    return schema.Result.ok(await dao.query_by_id(id))

@$router_name.get("", summary="分页条件查询")
async def query_${router_name}_all_by_limit(query: schema.$table = Depends(), page_number: int = 1, page_size: int = 10) -> schema.PageResult[schema.$table]:
    total = await dao.count(**query.model_dump(exclude_none=True))
    data = await dao.query_all_by_limit(**query.model_dump(exclude_none=True), page_number=page_number, page_size=page_size)
    return schema.PageResult.ok(data=data, total=total)       


@$router_name.post("", summary="新增数据")
async def create_${router_name}(instance: schema.$table) -> schema.Result[schema.$table]:
    return schema.Result.ok(await dao.create( instance))


@$router_name.patch("/{id}", summary="更新数据")
async def update_${router_name}_by_id(id: int, instance: schema.$table) -> schema.Result[schema.$table]:
    return schema.Result.ok(await dao.update(id, instance))


@$router_name.delete("/{id}", summary="删除数据")
async def delete_${router_name}_by_id(id: int) -> schema.Result[schema.$table]:
    return schema.Result.ok(await dao.delete_by_id( id))
"""


TORTOISE_MAIN = """
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from router import $router_name


app = FastAPI(title="DFS - FastAPI Tortoise ORM CRUD",
description='''
[![](https://img.shields.io/github/stars/zy7y/dfs-generate)](https://github.com/zy7y/dfs-generate)
[![](https://img.shields.io/github/forks/zy7y/dfs-generate)](https://github.com/zy7y/dfs-generate)
[![](https://img.shields.io/github/repo-size/zy7y/dfs-generate?style=social)](https://github.com/zy7y/dfs-generate)
[![](https://img.shields.io/github/license/zy7y/dfs-generate)](https://gitee.com/zy7y/dfs-generate/blob/master/LICENSE)

支持ORM：[SQLModel](https://sqlmodel.tiangolo.com/)、[Tortoise ORM](https://tortoise.github.io/)

支持前端: [Vue](https://cn.vuejs.org/)、[React](https://zh-hans.react.dev/)'''

)


register_tortoise(
        app,
        db_url="$uri",
        modules={"models": ["model"]},
        generate_schemas=False,
        add_exception_handlers=True,
    )


app.include_router($router_name)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", reload=True, port=5000)
"""
