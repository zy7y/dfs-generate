from typing import List, Optional

import black
import isort
from fastapi import FastAPI, Query
from fastapi.requests import Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from db import Conf, get_db_uri, get_metadata_by_db_uri
from generate import GenerateEntity, db_code_render, main_render, router_render
from schemas import ChangeDB, CodeGen, R, TableVO

app = FastAPI(
    title="dfs-generate",
    description="FastAPI SQLModel 逆向生成代码",
    docs_url=None,
    redoc_url=None,
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse("static/index.html")


@app.get("/tables")
def query_by_table_name_limit(
    request: Request, table_name: str = Query("", alias="tableName")
) -> R[Optional[List[TableVO]]]:
    total = []
    try:
        uri = Conf.get_db_uri_last_new()
        metadata = get_metadata_by_db_uri(uri)
        request.app.state.uri = uri
        request.app.state.metadata = metadata

        for _, table in metadata.tables.items():
            if table_name in table.name:
                total.append(
                    TableVO(table_name=table.name, table_comment=table.comment)
                )
        return R.success(data=total)

    except Exception as e:
        print(e)
    return R.error(msg="请先去配置数据库")


def black_with_isort_fmt_codes(data):
    for item in data:
        if v := item.get("code"):
            code = isort.code(v)
            item["code"] = black.format_str(code, mode=black.FileMode())
    return data


@app.get("/codegen", response_model=R[Optional[List[CodeGen]]])
def get_codegen_by_table_name(
    request: Request, table_name: str = Query(..., alias="tableName")
):
    try:
        table = request.app.state.metadata.tables[table_name]
        uri = request.app.state.uri
        data = [
            {"name": "model.py", "code": GenerateEntity(table).render()},
            {"name": "router.py", "code": router_render(table_name)},
            {"name": "main.py", "code": main_render(table_name)},
            {"name": "db.py", "code": db_code_render(uri)},
        ]
        black_with_isort_fmt_codes(data)
        return R.success(data=data)

    except Exception as e:
        print(e)
    return R.error(msg="表不存在 / 连接失败")


@app.post("/conf")
def change_db(conf: ChangeDB):
    uri = get_db_uri(**conf.model_dump())
    try:
        get_metadata_by_db_uri(uri)
        Conf.create(uri)
        return R.success(msg="设置成功")
    except Exception as e:
        print(e)
    return R.error(msg="请确认信息是否填写正确")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True, port=80)
