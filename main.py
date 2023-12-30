from fastapi import FastAPI, Query
from fastapi.requests import Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from entity import CodeGen, Conf, DBConf, R, RList, Table
from generate.main import generate_code

app = FastAPI(
    title="dfs-generate", description="FastAPI SQLModel 逆向生成代码", docs_url=None
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse("static/index.html")


@app.get("/tables", response_model=RList[Table])
def query_by_table_name_limit(
    request: Request, table_name: str = Query("", alias="tableName")
):
    total = []
    try:
        uri, metadata = Conf.get_last_uri_with_metadata()
        request.app.state.uri = uri
        request.app.state.metadata = metadata
        for _, table in metadata.tables.items():
            if table_name in table.name:
                total.append(dict(table_name=table.name, table_comment=table.comment))
        return RList.success(data=total)

    except Exception as e:
        print(e)
    return RList.error(msg="请先去配置数据库")


@app.get("/codegen", response_model=RList[CodeGen])
def get_codegen_by_table_name(
    request: Request, table_name: str = Query(..., alias="tableName")
):
    try:
        table = request.app.state.metadata.tables[table_name]
        uri = request.app.state.uri

        return RList.success(data=generate_code(table, uri))

    except Exception as e:
        print(e)
    return RList.error(msg="表不存在 / 连接失败")


@app.post("/conf")
def change_db(conf: DBConf):
    try:
        conf.get_metadata()
        Conf.create(conf.get_db_uri())
        return R.success(msg="设置成功")
    except Exception as e:
        print(e)
    return R.error(msg="请确认信息是否填写正确")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True, port=80)
