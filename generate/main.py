from generate.model import GenerateEntity, Table, to_pascal

main_template = """
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html

from router import {table_name}_router

app = FastAPI()


@app.get("/docs", include_in_schema=False)
def docs():
    return get_swagger_ui_html(
        swagger_js_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.6.2/swagger-ui-bundle.min.js",
        swagger_css_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.6.2/swagger-ui.min.css"
    )


app.include_router({table_name}_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", reload=True, port=5000)

"""


def render_main(table_name):
    return main_template.format(table_name=table_name)


db_template = """
from sqlmodel import create_engine

db_uri = "{db_uri}"

engine = create_engine(db_uri)
"""


def render_db(db_uri):
    """数据库链接- sqlalchemy"""
    return db_template.format(db_uri=db_uri)


router_template = """
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
        total = {pascal_name}.count(session, **query.count_kwargs(exclude_none=True))
        data = {pascal_name}.query_all_by_limit(session, **query.model_dump(exclude_none=True))
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


def render_router(table_name):
    router_code = router_template.format(
        table_name=table_name, pascal_name=to_pascal(table_name), id="{id}"
    )
    return router_code


def generate_code(table: Table, uri: str):
    return [
        {"name": "model.py", "code": GenerateEntity(table).render()},
        {"name": "router.py", "code": render_router(table.name)},
        {"name": "main.py", "code": render_main(table.name)},
        {"name": "db.py", "code": render_db(uri)},
    ]
