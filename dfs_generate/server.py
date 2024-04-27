import os
from typing import Dict

import bottle
import isort
from yapf.yapflib.yapf_api import FormatCode

from dfs_generate.conversion import SQLModelConversion, TortoiseConversion
from dfs_generate.tools import MySQLConf, MySQLHelper

app = bottle.Bottle()

CACHE: Dict[str, MySQLHelper] = {}

# 解决打包桌面程序static找不到的问题
static_file_abspath = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "web", "dist"
)
print(static_file_abspath)


@app.hook("before_request")
def validate():
    request_method = bottle.request.environ.get("REQUEST_METHOD")
    access_control = bottle.request.environ.get("HTTP_ACCESS_CONTROL_REQUEST_METHOD")
    if request_method == "OPTIONS" and access_control:
        bottle.request.environ["REQUEST_METHOD"] = access_control


@app.hook("after_request")
def enable_cors():
    bottle.response.headers["Access-Control-Allow-Origin"] = "*"
    bottle.response.headers["Access-Control-Allow-Headers"] = "*"


# 定义路由，提供静态文件服务
@app.get("/static/<filepath:path>")
def serve_static(filepath):
    return bottle.static_file(filepath, root=static_file_abspath)


# 定义首页路由
@app.get("/")
def index():
    with open(os.path.join(static_file_abspath, "index.html"), "rb") as f:
        html_content = f.read()
    bottle.response.content_type = "text/html"
    return html_content


@app.post("/conf")
def connect():
    payload = bottle.request.json
    if payload:
        conf = MySQLConf(**payload)
        CACHE["connect"] = MySQLHelper(conf)
        return {"code": 20000, "msg": "ok", "data": None}


@app.get("/tables")
def tables():
    if obj := CACHE.get("connect"):
        like = bottle.request.query.get("tableName")
        data = [
            {"tableName": table, "key": table}
            for table in obj.get_tables()
            if like in table
        ]
        return {"code": 20000, "msg": "ok", "data": data}
    return []


@app.get("/codegen")
def codegen():
    obj = CACHE.get("connect")
    table = bottle.request.query.get("tableName")
    mode = bottle.request.query.get("mode")
    results = []
    if mode == "sqlmodel":
        _instance = SQLModelConversion
    else:
        _instance = TortoiseConversion

    data = _instance(
        table, obj.get_table_columns(table), obj.conf.get_db_uri()
    ).gencode()

    for k, v in data.items():
        _code = FormatCode(v, style_config="pep8")[0]
        v = isort.code(_code)
        results.append({"name": k, "code": v, "key": k})
    return {"code": 20000, "msg": "ok", "data": results}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True, reloader=True)
