from pydantic.alias_generators import to_pascal

template = """
{table_name}_router = APIRouter(prefix="/{table_name}", tags=["{table_name}"])


@{table_name}_router.get("/{id}", summary="通过ID查询详情")
def query_{table_name}_by_id(id: int) -> Result[{model}]:
    with Session(engine) as session:
        return Result.ok({model}.get_by_id(session, id))


@{table_name}_router.get("", summary="分页条件查询")
def query_{table_name}_all_by_limit(query: {model}Query = Depends()) -> PageResult[{model}]:
    with Session(engine) as session:
        return PageResult.ok({model}.query_all_by_limit(session, **query.model_dump(exclude_unset=True)))


@{table_name}_router.post("", summary="新增数据")
def create_{table_name}(instance: {model_do}) -> Result[{model}]:
    with Session(engine) as session:
        return Result.ok({model}.create(session, instance))


@{table_name}_router.patch("/{id}", summary="更新数据")
def update_{table_name}_by_id(id: int, instance: {model_do}) -> Result[{model}]:
    with Session(engine) as session:
        return Result.ok({model}.update(session, id, instance))


@{table_name}_router.delete("/{id}", summary="删除数据")
def delete_{table_name}_by_id(id: int) -> Result[{model}]:
    with Session(engine) as session:
        return Result.ok({model}.delete_by_id(session, id))
"""


def render(table_name):
    pascal_table_name = to_pascal(table_name)
    import_code = f"""
from fastapi import APIRouter, Depends
from sqlmodel import Session
from model import {pascal_table_name}DTO, {pascal_table_name}, Result, PageResult, {pascal_table_name}Query
from db import engine
        """

    router_code = template.format(
        table_name=table_name,
        model=pascal_table_name,
        model_do=pascal_table_name + "DTO",
        id="{id}",
    )
    return import_code + router_code
