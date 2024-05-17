DOC_DESC = """
[![](https://img.shields.io/github/stars/zy7y/dfs-generate)](https://github.com/zy7y/dfs-generate)
[![](https://img.shields.io/github/forks/zy7y/dfs-generate)](https://github.com/zy7y/dfs-generate)
[![](https://img.shields.io/github/repo-size/zy7y/dfs-generate?style=social)](https://github.com/zy7y/dfs-generate)
[![](https://img.shields.io/github/license/zy7y/dfs-generate)](https://gitee.com/zy7y/dfs-generate/blob/master/LICENSE)

支持ORM：[SQLModel](https://sqlmodel.tiangolo.com/)、[Tortoise ORM](https://tortoise.github.io/)

支持前端: [Vue](https://cn.vuejs.org/)
"""

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

class PageParam(BaseModel):
    page_number: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页数量")

    model_config = {"alias_generator": to_camel, "populate_by_name": True}

"""

SQLMODEL_DAO = """
def create(session: Session, obj_in: schema.{table}) -> model.{table}:
    obj = model.{table}(**obj_in.model_dump(exclude_unset=True))
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj

def query_by_id(session: Session, id: int) -> Optional[model.{table}]:
    return session.get(model.{table}, {pk})

def update(session: Session, id: int, obj_in: schema.{table}) -> Optional[model.{table}]:
    obj = query_by_id(session, id)
    if obj:
        for field, value in obj_in.model_dump(exclude_unset=True).items():
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
def query_${router_name}_all_by_limit(query: schema.$table = Depends(), page: schema.PageParam = Depends()) -> schema.PageResult[schema.$table]:
    with Session(engine) as session:
        total = dao.count(session, **query.model_dump(exclude_none=True))
        data = dao.query_all_by_limit(session, **query.model_dump(exclude_none=True), page_number=page.page_number, page_size=page.page_size)
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

SQLMODEL_MAIN = (
    """
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


from router import {router_name}


app = FastAPI(title="DFS - FastAPI SQLModel CRUD", 
description='''%s''')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router({router_name})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", reload=True, port=5000)
"""
    % DOC_DESC
)


# Tortoise ORM

TORTOISE_DAO = """
async def create(obj_in: schema.{table}) -> model.{table}:
    obj = model.{table}(**obj_in.model_dump(exclude_unset=True))
    await obj.save()
    return obj

async def query_by_id(id: int) -> Optional[model.{table}]:
    return await model.{table}.get_or_none({pk})

async def update(id: int, obj_in: schema.{table}) -> Optional[model.{table}]:
    obj= await query_by_id(id)
    if obj:
        for field, value in obj_in.model_dump(exclude_unset=True).items():
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
async def query_${router_name}_all_by_limit(query: schema.$table = Depends(), page: schema.PageParam = Depends()) -> schema.PageResult[schema.$table]:
    total = await dao.count(**query.model_dump(exclude_none=True))
    data = await dao.query_all_by_limit(**query.model_dump(exclude_none=True), page_number=page.page_number, page_size=page.page_size)
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


TORTOISE_MAIN = (
    """
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from router import $router_name


app = FastAPI(title="DFS - FastAPI Tortoise ORM CRUD",description='''%s''')


register_tortoise(
        app,
        db_url="$uri",
        modules={"models": ["model"]},
        generate_schemas=False,
        add_exception_handlers=True,
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router($router_name)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", reload=True, port=5000)
"""
    % DOC_DESC
)

# Vue
VUE_CRUD_TS = """
/**
 * dfs-generate 生成FastAPI Tortoise ORM / SQLModel、Vue3 CRUD代码
 * dfs-generate Github: https://github.com/zy7y/dfs-generate
 * Vue CRUD代码基于fast-crud，更多用法请查看其官方文档 http://fast-crud.docmirror.cn/ 
 */
import { CreateCrudOptionsProps, CreateCrudOptionsRet, dict } from "@fast-crud/fast-crud";
import { addRequest, delRequest, editRequest, pageRequest } from "./api";

export default function ({ crudExpose, context }: CreateCrudOptionsProps<any>): CreateCrudOptionsRet<any> {
  return {
    crudOptions: {
      request: {
        pageRequest,
        addRequest,
        editRequest,
        delRequest
      },
      columns: %s
    }
  };
}

"""

VUE_API_TS = """
/**
 * dfs-generate 生成FastAPI Tortoise ORM / SQLModel、Vue3 CRUD代码
 * dfs-generate Github: https://github.com/zy7y/dfs-generate
 * Vue CRUD代码基于fast-crud，更多用法请查看其官方文档 http://fast-crud.docmirror.cn/
 */
import { AddReq, DelReq, EditReq, UserPageQuery, UserPageRes } from "@fast-crud/fast-crud";
import axios from "axios";

const url = "http://127.0.1:5000/%s";

export const pageRequest = async (query: UserPageQuery): Promise<UserPageRes> => {
  const { limit, offset } = query.page;
  const pageNumber = offset / limit + 1;
  const pageSize = limit;
  const res = await axios.get(url, {
    params: {
      pageNumber,
      pageSize,
      ...query.query
    }
  });
  return {
    records: res.data.data,
    ...query.page,
    total: res.data.total
  };
};
export const editRequest = async ({ form, row }: EditReq) => {
  const res = await axios.patch(url + "/" + row.id, form, {
    headers: {
      "Content-Type": "application/json"
    }
  });
  return res.data.data;
};
export const delRequest = async ({ row }: DelReq) => {
  const res = await axios.delete(url + "/" + row.id);
  return res.data.data;
};

export const addRequest = async ({ form }: AddReq) => {
  const res = await axios.post(url, form, {
    headers: {
      "Content-Type": "application/json"
    }
  });
  return res.data.data;
};

"""

VUE_INDEX_VUE = """
<!-- 
dfs-generate 生成FastAPI Tortoise ORM / SQLModel、Vue3 CRUD代码
dfs-generate Github: https://github.com/zy7y/dfs-generate
Vue CRUD代码基于fast-crud，更多用法请查看其官方文档 http://fast-crud.docmirror.cn/ 
-->
<template>
  <fs-page>
    <fs-crud ref="crudRef" v-bind="crudBinding" />
  </fs-page>
</template>

<script lang="ts">
import { defineComponent, onMounted } from "vue";
import { useFs, OnExposeContext } from "@fast-crud/fast-crud";
import createCrudOptions from "./crud";

//此处为组件定义
export default defineComponent({
  name: "FsCrud%s",
  setup(props: any, ctx: any) {
    const context: any = { props, ctx }; // 自定义变量, 将会传递给createCrudOptions, 比如直接把props,和ctx直接传过去使用
    function onExpose(e: OnExposeContext) {} //将在createOptions之前触发，可以获取到crudExpose,和context
    const { crudRef, crudBinding, crudExpose } = useFs<any>({ createCrudOptions, onExpose, context });

    // 页面打开后获取列表数据
    onMounted(() => {
      crudExpose.doRefresh();
    });
    return {
      crudBinding,
      crudRef
    };
  }
});
</script>
"""
