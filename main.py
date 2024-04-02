import os
import uuid
from typing import Any, Dict, Generic, List, Optional, Sequence, TypeVar

import isort
from fastapi import FastAPI, Query
from fastapi.requests import Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, ConfigDict, field_serializer
from pydantic.alias_generators import to_camel, to_pascal, to_snake
from sqlmodel import (DATETIME, Column, Field, MetaData, Session, SQLModel,
                      Table, create_engine, select)
from yapf.yapflib.yapf_api import FormatCode


class Analysis:

    def __init__(self, table: Table):
        self.table = table
        self.do_fields = []
        self.dto_fields = []
        self.query_fields = []
        self.imports = set()

    def _column_type_parse(self, column: Column):
        """
        解析column type
        """
        python_type = column.type.python_type
        module_name = python_type.__module__
        class_name = python_type.__name__
        if module_name not in ["__builtin__", "builtins"]:
            self.imports.add(f"from {module_name} import {class_name}")

        c_type = column.type.__dict__
        kwargs = {}
        if v := c_type.get("length"):
            kwargs["max_length"] = v
        if v := c_type.get("precision"):
            kwargs["max_digits"] = v
        if v := c_type.get("scale"):
            kwargs["decimal_places"] = v
        if class_name == "dict":
            self.imports.add("from sqlmodel import JSON")
            kwargs["sa_type"] = "JSON"
        return kwargs

    def _column_default_datetime(self, text: str):
        """https://github.com/tiangolo/sqlmodel/issues/594"""
        _current = "CURRENT_TIMESTAMP"
        if _current in text and "ON UPDATE" in text:
            self.imports.add("from sqlmodel import func, DateTime, Column")
            return {"sa_column": "Column(DateTime(), onupdate=func.now())"}
        if _current in text:
            return {"default_factory": "datetime.utcnow"}
        return {"default": text}

    def _column_default_parse(self, column: Column):
        """解析 column 默认值"""
        if column.server_default:
            text = column.server_default.arg.text
            if isinstance(column.type, DATETIME):
                return self._column_default_datetime(text)
            elif column.type.python_type.__name__ == "int":
                return {"default": text.replace("'", "")}
            else:
                return {"default": text}

    def field_all_attrs(self, column: Column) -> dict:
        kwargs = {"default": None, **self._column_type_parse(column)}

        # 是否可以为空
        if v := column.nullable:
            kwargs["nullable"] = v
        else:
            kwargs["default"] = "..."

        # 默认值
        if v := self._column_default_parse(column):
            kwargs.update(v)
        # 主键
        if column.primary_key:
            kwargs["primary_key"] = True
            kwargs["default"] = None

        # 索引
        if column.index:
            kwargs["index"] = True

        # 唯一
        if column.unique:
            kwargs["unique"] = True

        # 描述
        if desc := column.comment:
            kwargs["description"] = '"' + desc + '"'

        if "default_factory" in kwargs:
            kwargs.pop("default")

        if "sa_column" in kwargs:
            kwargs.pop("nullable")
        return kwargs

    def get_field_repr(
        self, field_name: str, field_type: str, field_attrs: Dict[str, Any]
    ) -> str:
        """字段信息
        https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/?h=optional#optional-fields-nullable-columns
        :param field_name: 字段名称
        :param field_type: 字段类型
        :param field_attrs: 字段其他属性
        return name: str = Field(..., max_length=22)
        """
        if (
            "func.now" not in field_attrs.get("sa_column", "")
            and field_attrs.get("default", "") is None
        ):
            field_type = f"Optional[{field_type}]"

        head = f"{field_name}:{field_type}=Field("
        tail = ",".join(f"{k}={v}" for k, v in field_attrs.items()) + ")"
        return head + tail

    def get_optional_field_repr(
        self, field_name: str, field_type: str, field_attrs: Dict[str, Any]
    ) -> str:
        if field_attrs.get("default") is None:
            field_type = f"Optional[{field_type}]"

        head = f"{field_name}:{field_type}=Field("
        tail = ",".join(f"{k}={v}" for k, v in field_attrs.items()) + ")"
        return head + tail

    def _add_query_field(
        self, filed_name: str, field_type: str, kwargs: Dict[str, Any]
    ):
        _qf_kwargs = {"default": None}
        for k, v in kwargs.items():
            if k in ["max_length", "max_digits", "decimal_places", "description"]:
                _qf_kwargs[k] = v
        self.query_fields.append(
            self.get_optional_field_repr(filed_name, field_type, _qf_kwargs)
        )

    def add_field_by_column(self, column: Column):
        field_name = column.name
        field_type = column.type.python_type.__name__
        field_attrs = self.field_all_attrs(column)
        field_repr = self.get_field_repr(field_name, field_type, field_attrs)
        if column.primary_key:
            self.do_fields.append(field_repr)
        else:
            self.dto_fields.append(field_repr)
            if (
                not column.nullable
                or "datetime.utcnow" in field_repr
                or "func.now" in field_repr
            ):
                self._add_query_field(field_name, field_type, field_attrs)

    def add_dto_head_field(self):
        do_annotation = f'"""{self.table.comment or self.table.description}"""'
        do_metadata = f'__tablename__ = "{self.table.name}"'
        self.do_fields.append(do_annotation)
        self.do_fields.append(do_metadata)

    def add_do_tail_field(self):
        self.imports.add("from pydantic.alias_generators import to_camel")
        self.imports.add("from sqlmodel import SQLModel, Field")
        self.dto_fields.append(
            'model_config = {"alias_generator": to_camel, "populate_by_name": True}'
        )

    def render_fields_str(self, fields: Sequence[str], use_indent=True) -> str:
        if use_indent:
            return "\n".join(self.indent + field for field in fields)
        else:
            return "\n".join(field for field in fields)

    def render(self):
        """生成model code"""
        self.add_dto_head_field()
        for column in self.table.columns:
            self.add_field_by_column(column)
        self.add_do_tail_field()
        return {
            "table_name": self.table.name,
            "imports": self.imports,
            "dto_fields": self.dto_fields,
            "do_fields": self.do_fields,
            "query_fields": self.query_fields,
            "default_exclude": "{'page_number', 'page_size'}",
        }


env = Environment(loader=FileSystemLoader("templates"))
env.filters["to_snake"] = to_snake
env.filters["to_pascal"] = to_pascal


def generate_code(table: Table, uri: str):
    name = {"table": table.name}
    main = env.get_template("main.j2").render(name)
    router = env.get_template("router.j2").render(name)
    db = env.get_template("db.j2").render({"uri": uri})
    model = env.get_template("model.j2").render(Analysis(table).render())

    return [
        {"name": "model.py", "code": model},
        {"name": "router.py", "code": router},
        {"name": "main.py", "code": main},
        {"name": "db.py", "code": db},
    ]


db_uri = "sqlite:///main.sqlite"
engine = create_engine(db_uri)


def get_metadata_by_db_uri(uri: str):
    db_engine = create_engine(uri)
    db_metadata = MetaData()
    db_metadata.reflect(bind=db_engine)
    return db_metadata


class Conf(SQLModel, table=True):
    __tablename__ = "dfs_conf"
    id: int = Field(None, primary_key=True)
    db_uri: str = Field(..., description="数据库连接")

    @classmethod
    def get_db_uri_last_new(cls):
        """获取最新的db_url"""
        with Session(engine) as session:
            query = select(cls).order_by(cls.id.desc())
            latest_conf = session.exec(query).first()
            if latest_conf:
                return latest_conf.db_uri
            else:
                return None

    @classmethod
    def create(cls, uri) -> "Conf":
        with Session(engine) as session:
            obj = cls(db_uri=uri)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj

    @classmethod
    def get_last_uri_with_metadata(cls):
        uri = cls.get_db_uri_last_new()
        return uri, get_metadata_by_db_uri(uri)


SQLModel.metadata.create_all(engine)

T = TypeVar("T")


class R(BaseModel, Generic[T]):
    code: int = 20000
    msg: str = "ok"
    data: Optional[T] = None

    @classmethod
    def success(cls, **kwargs):
        return cls(**kwargs)

    @classmethod
    def error(cls, msg):
        return cls(code=40000, msg=msg)


class RList(R[T]):
    data: List[T] = Field(default_factory=list)


class BaseVo(SQLModel):
    key: uuid.UUID = Field(default_factory=uuid.uuid4)
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class Table(BaseVo):
    table_name: str
    table_comment: Optional[str] = None


class DBConf(SQLModel):
    user: str
    password: str
    port: int
    host: str
    db: str

    def get_db_uri(self):
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    def get_metadata(self):
        return get_metadata_by_db_uri(self.get_db_uri())


class CodeGen(BaseVo):
    name: str
    code: str

    @field_serializer("code")
    def serialize_code(self, code: str, _info):
        _code = FormatCode(code, style_config="pep8")[0]
        return isort.code(_code)


###    API

app = FastAPI(title="dfs-generate", description="FastAPI SQLModel 逆向生成代码")

# 解决打包桌面程序static找不到
static_file_abspath = os.path.join(os.path.dirname(__file__), "static")

app.mount("/static", StaticFiles(directory=static_file_abspath), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(f"{static_file_abspath}/index.html")


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


import random
import socket
import threading

import uvicorn
import webview

# client


def get_unused_port():
    """获取未被使用的端口"""
    while True:
        port = random.randint(1024, 65535)  # 端口范围一般为1024-65535
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("localhost", port))
            sock.close()
            return port
        except OSError:
            pass


def desktop_client():
    port = get_unused_port()
    t = threading.Thread(target=uvicorn.run, args=(app,), kwargs={"port": port})
    t.daemon = True
    t.start()
    webview.create_window("DFS代码生成", url=f"http://127.0.0.1:{port}")
    webview.start()


if __name__ == "__main__":
    desktop_client()
