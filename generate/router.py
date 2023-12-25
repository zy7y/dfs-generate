from pydantic.alias_generators import to_pascal

template = """
from fastapi import APIRouter, Depends
from sqlmodel import Session
from model import {pascal_name}DTO, {pascal_name}, Result, PageResult, {pascal_name}Query
from db import engine

{table_name}_router = APIRouter(prefix="/{table_name}", tags=["{table_name}"])

@{table_name}_router.get("/{id}", summary="通过ID查询详情")
def query_{table_name}_by_id(id: int) -> Result[{pascal_name}]:
    with Session(engine) as session:
        return Result.ok({pascal_name}.query_by_id(session, id))

@{table_name}_router.get("", summary="分页条件查询")
def query_{table_name}_all_by_limit(query: {pascal_name}Query = Depends()) -> PageResult[{pascal_name}]:
    with Session(engine) as session:
        total = {pascal_name}.count(session)
        data = {pascal_name}.query_all_by_limit(session, **query.model_dump(exclude_unset=True))
        return PageResult.ok(data=data, total=total)


@{table_name}_router.post("", summary="新增数据")
def create_{table_name}(instance: {pascal_name}DTO) -> Result[{pascal_name}]:
    with Session(engine) as session:
        return Result.ok({pascal_name}.create(session, instance))


@{table_name}_router.patch("/{id}", summary="更新数据")
def update_{table_name}_by_id(id: int, instance: {pascal_name}DTO) -> Result[{pascal_name}]:
    with Session(engine) as session:
        return Result.ok({pascal_name}.update(session, id, instance))


@{table_name}_router.delete("/{id}", summary="删除数据")
def delete_{table_name}_by_id(id: int) -> Result[{pascal_name}]:
    with Session(engine) as session:
        return Result.ok({pascal_name}.delete_by_id(session, id))
"""


def render(table_name):
    router_code = template.format(
        table_name=table_name,
        pascal_name=to_pascal(table_name),
        id="{id}"
    )
    return router_code
