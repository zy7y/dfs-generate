import os

import bottle
import isort
from yapf.yapflib.yapf_api import FormatCode

from dfs_generate.conversion import SQLModelConversion, TortoiseConversion
from dfs_generate.tools import Cache, MySQLConf, MySQLHelper

app = bottle.Bottle()
cache = Cache()
cache.start()

# 解决打包桌面程序static找不到的问题
static_file_abspath = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "web", "dist"
)


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


# 连接数据库
@app.get("/con")
def connect():
    if cache.get():
        return {"code": 20000, "msg": "ok", "data": cache.get()}
    return {"code": 40000, "msg": "error", "data": None}


@app.post("/conf")
def configure():
    payload = bottle.request.json
    try:
        with MySQLHelper(MySQLConf(**payload)):
            cache.set(**MySQLConf(**payload).json())
        return {"code": 20000, "msg": "ok", "data": None}
    except Exception as e:
        return {"code": 40000, "msg": str(e), "data": None}


@app.get("/tables")
def get_tables():
    like = bottle.request.query.get("tableName")
    try:
        with MySQLHelper(MySQLConf(**cache.get())) as obj:
            data = [
                {"tableName": table, "key": table}
                for table in obj.get_tables()
                if like in table
            ]
            return {"code": 20000, "msg": "ok", "data": data}
    except Exception as e:
        return {"code": 40000, "msg": str(e), "data": None}


@app.get("/codegen")
def codegen():
    table = bottle.request.query.get("tableName")
    mode = bottle.request.query.get("mode")
    results = []
    if mode == "sqlmodel":
        _instance = SQLModelConversion
    else:
        _instance = TortoiseConversion
    try:
        with MySQLHelper(MySQLConf(**cache.get())) as obj:
            data = _instance(
                table, obj.get_table_columns(table), obj.conf.db_uri
            ).gencode()
    except Exception as e:
        return {"code": 40000, "msg": str(e), "data": None}

    for k, v in data.items():
        if k.endswith("py"):
            _code = FormatCode(v, style_config="pep8")[0]
            v = isort.code(_code)
        results.append({"name": k, "code": v, "key": k})
    return {"code": 20000, "msg": "ok", "data": results}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True, reloader=True)
