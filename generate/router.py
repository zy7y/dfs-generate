from pydantic.alias_generators import to_pascal

imports = {
    "from typing import Optional, List",
    "from fastapi import APIRouter",
    "from sqlmodel import Session",
}

template = """
{table_name}_router = APIRouter(prefix="/{table_name}", tags=["{table_name}"])


@{table_name}_router.get("/{id}", summary="通过ID查询详情")
def query_{table_name}_by_id(id: int) -> Optional[{model}]:
    with Session(engine) as session:
        return {model}.get_by_id(session, id)


@{table_name}_router.get("", summary="分页条件查询")
def query_{table_name}_all_by_limit(limit: int = 1, offset: int = 10, **kwargs) -> List[{model}]:
    with Session(engine) as session:
        return {model}.find_with_pagination(session, limit, offset, **kwargs)


@{table_name}_router.post("", summary="新增数据")
def create_{table_name}(instance: {model_do}) -> {model}:
    with Session(engine) as session:
        return {model}.create(session, instance)


@{table_name}_router.patch("/{id}", summary="更新数据")
def update_{table_name}_by_id(id: int, instance: {model_do}) -> {model}:
    with Session(engine) as session:
        return {model}.update(session, id, instance)


@{table_name}_router.delete("/{id}", summary="删除数据")
def delete_{table_name}_by_id(id: int) -> Optional[{model}]:
    with Session(engine) as session:
        return {model}.delete_by_id(session, id)
"""


def render(table_name):
    pascal_table_name = to_pascal(table_name)
    model_import = f"from model import {pascal_table_name}DO, {pascal_table_name}"
    db_import = f"from db import engine"
    imports.add(model_import)
    imports.add(db_import)

    router_code = template.format(
        table_name=table_name,
        model=pascal_table_name,
        model_do=pascal_table_name + "DO",
        id="{id}",
    )
    return "\n".join(im for im in imports) + router_code
