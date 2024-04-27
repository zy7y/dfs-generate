from string import Template

from tpl import SQLMODEL_DAO, TORTOISE_DAO, RESPONSE_SCHEMA, SQLMODEL_ROUTER, MAIN
from tools import to_pascal, tran, to_snake


def _pydantic_field(column, imports):
    # 列名
    name = column["COLUMN_NAME"]
    # 类型
    t = column["DATA_TYPE"]
    info = tran(t, "pydantic")
    end = "None"
    if desc := column["COLUMN_COMMENT"]:
        end = f"Field(None, description='{desc}')"
        imports.add("from pydantic import Field")
    field = f"{name}: Optional[{info['type']}] = {end}"
    if info["import"]:
        imports.add(info["import"])
    return field


class Conversion:
    def __init__(self, table_name, columns):
        self.table_name = table_name
        self.columns = columns

    @property
    def table(self):
        return to_pascal(self.table_name)

    @property
    def router_name(self):
        return to_snake(self.table_name)

    def model(self):
        pass

    def dao(self):
        pass

    def schema(self):
        imports = {
            "from typing import Optional",
            "from pydantic import BaseModel, Field",
            "from pydantic.alias_generators import to_camel",
        }
        head = f"class {self.table}(BaseModel):"
        fields = []
        for column in self.columns:
            field = _pydantic_field(column, imports)
            if "    " + field not in fields:
                fields.append("    " + field)
        fields.append(
            "    "
            + 'model_config = {"alias_generator": to_camel, "populate_by_name": True}'
        )
        return (
            "\n".join(imports)
            + "\n\n"
            + RESPONSE_SCHEMA
            + "\n\n"
            + head
            + "\n"
            + "\n".join(fields)
            + "\n"
        )

    def router(self):
        pass

    def main(self):
        return MAIN.format(router_name=self.router_name)

    def gencode(self):
        return {
            "model.py": self.model(),
            "dao.py": self.dao(),
            "router.py": self.router(),
            "schema.py": self.schema(),
            "main.py": self.main(),
        }


def _sqlmodel_field_repr(column, imports):
    # 列名
    info = tran(column["DATA_TYPE"], "pydantic")
    _type = info["type"]
    if imported := info["import"]:
        imports.add(imported)
    kwargs = {"default": None}
    if v := column["CHARACTER_MAXIMUM_LENGTH"]:
        kwargs["max_length"] = v
    if v := column["NUMERIC_PRECISION"] and _type == "Decimal":
        kwargs["max_digits"] = v
    if v := column["NUMERIC_SCALE"] and _type == "Decimal":
        kwargs["decimal_places"] = v
    if _type == "dict":
        imports.add("from sqlmodel import JSON")
        kwargs["sa_type"] = "JSON"

    if column["IS_NULLABLE"] == "YES":
        kwargs["nullable"] = True
    else:
        kwargs["default"] = "..."

    if v := column["COLUMN_DEFAULT"]:
        if _type == "int":
            kwargs["default"] = v

    # 主键
    if column["COLUMN_KEY"] == "PRI":
        kwargs["primary_key"] = True
        kwargs["default"] = None

    # 描述
    if desc := column["COLUMN_COMMENT"]:
        kwargs["description"] = '"' + desc + '"'

    if column["EXTRA"] == "DEFAULT_GENERATED":
        imports.add("from datetime import datetime")
        kwargs.update({"default_factory": "datetime.utcnow"})

    elif column["EXTRA"].startswith("DEFAULT_GENERATED on update"):
        imports.add("from sqlmodel import func, DateTime, Column")
        kwargs.update({"sa_column": "Column(DateTime(), onupdate=func.now())"})

    if column["COLUMN_KEY"] == "MUL":
        kwargs["index"] = True

    if column["COLUMN_KEY"] == "UNI":
        kwargs["unique"] = True

    if "default_factory" in kwargs:
        kwargs.pop("default")

    if "sa_column" in kwargs and "nullable" in kwargs:
        kwargs.pop("nullable")

    name = column["COLUMN_NAME"]
    if kwargs.get("default", "") is None and "func.now" not in kwargs.get(
        "sa_column", ""
    ):
        imports.add("from typing import Optional")
        field_type = f"Optional[{_type}]"
    else:
        field_type = info["type"]
    head = f"{name}: {field_type} = Field("
    tail = ",".join(f"{k}={v}" for k, v in kwargs.items()) + ")"
    return head + tail


class SQLModelConversion(Conversion):
    def model(self):
        imports = {"from sqlmodel import SQLModel, Field"}
        head = f"class {self.table}(SQLModel, table=True):"
        fields = []
        for column in self.columns:
            field = _sqlmodel_field_repr(column, imports)
            if "    " + field not in fields:
                fields.append("    " + field)
        return "\n".join(imports) + "\n\n" + head + "\n" + "\n".join(fields)

    def dao(self):
        imports = {
            "from sqlmodel import Session, SQLModel,select, func, Field",
            "from typing import List, Optional",
            "import model",
            "import schema",
        }
        content = SQLMODEL_DAO.format(table=self.table)
        return "\n".join(imports) + "\n\n" + content

    def router(self):
        return Template(SQLMODEL_ROUTER).safe_substitute(
            router_name=self.router_name, table=self.table
        )


def _tortoise_field_repr(column):
    name = column["COLUMN_NAME"]
    info = tran(column["DATA_TYPE"], "tortoise-orm")
    kwargs = {}
    if v := column["IS_NULLABLE"] == "YES":
        kwargs["null"] = v
    if v := column["CHARACTER_MAXIMUM_LENGTH"]:
        kwargs["max_length"] = v

    if v := column["NUMERIC_PRECISION"] and info["type"] == "Decimal":
        kwargs["max_digits"] = v

    if v := column["NUMERIC_SCALE"] and info["type"] == "Decimal":
        kwargs["decimal_places"] = v

    if v := column["COLUMN_DEFAULT"]:
        if info["type"] == "int":
            kwargs["default"] = v
        else:
            kwargs["default"] = f"{v}"
    if v := column["COLUMN_COMMENT"]:
        kwargs["description"] = f'"{v}"'

    if column["COLUMN_KEY"] == "MUL":
        kwargs["index"] = True

    if column["EXTRA"] == "DEFAULT_GENERATED":
        kwargs["auto_now_add"] = True
        if "default" in kwargs:
            kwargs.pop("default")

    if column["EXTRA"].startswith("DEFAULT_GENERATED on update"):
        kwargs["auto_now"] = True
        if "default" in kwargs:
            kwargs.pop("default")

    if column["COLUMN_KEY"] == "UNI":
        kwargs["unique"] = True

    if column["COLUMN_KEY"] == "PRI":
        kwargs["pk"] = True

    return f"{name} = fields.{info['type']}({', '.join(f'{k}={v}' for k, v in kwargs.items())})"


class TortoiseConversion(Conversion):
    def model(self):
        imports = {"from tortoise import Model, fields"}
        head = f"class {self.table}(Model):"
        fields = []
        for column in self.columns:
            field = _tortoise_field_repr(column)
            if "    " + field not in fields:
                fields.append("    " + field)
        return "\n".join(imports) + "\n\n" + head + "\n" + "\n".join(fields)

    def dao(self):
        imports = {"from typing import List, Optional", "import model", "import schema"}
        content = TORTOISE_DAO.format(table=self.table)
        return "\n".join(imports) + "\n\n" + content
