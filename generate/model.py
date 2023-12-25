from pydantic.alias_generators import to_pascal
from sqlmodel import DATETIME, Column, Table


class GenerateSQLModel:
    template = """
{imports}
from typing import Generic, TypeVar, List, Optional
from sqlmodel import Session, SQLModel,select, func, Field
from pydantic import BaseModel
from pydantic.alias_generators import to_camel
T = TypeVar('T')
class Result(BaseModel, Generic[T]):
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="额外消息")
    data: Optional[T] = Field(None, description="响应数据")

    @classmethod
    def ok(cls, data: T, message: str="成功"):
        return cls(data=data, message=message, success=True)

    @classmethod
    def error(cls, message: str = "失败"):
        return cls(data=None, message=message, success=False)

class PageResult(Result[T]):
    total: int = Field(0, description="数据总数")
    data: List[T] = Field(default_factory=list, description="响应数据")

    @classmethod
    def ok(cls, data: List[T], total: int, message: str = "成功"):
        return cls(data=data, total=total, message=message, success=True)

class {table_name}DTO(SQLModel):\n{fields}\n    {model_config}
class {table_name}Query(SQLModel):
    page_number: int = Field(1, description="页码")
    page_size: int = Field(10, description="页量")
    {model_config}
    

class {table_name}({table_name}DTO, table=True):\n{primary_key_field}\n
    @classmethod
    def create(cls, session: Session, obj_in: {table_name}DTO) -> "{table_name}":
        obj = cls(**obj_in.dict())
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    @classmethod
    def query_by_id(cls, session: Session, id: int) -> Optional["{table_name}"]:
        return session.get(cls, id)

    @classmethod
    def update(cls, session: Session, id: int, obj_in: {table_name}DTO) -> Optional["{table_name}"]:
        obj = cls.get_by_id(session, id)
        if obj:
            for field, value in obj_in.dict(exclude_unset=True).items():
                setattr(obj, field, value)
            session.add(obj)
            session.commit()
            session.refresh(obj)
        return obj

    @classmethod
    def delete_by_id(cls, session: Session, id: int) -> Optional["{table_name}"]:
        obj = session.get(cls, id)
        if obj:
            session.delete(obj)
            session.commit()
        return obj
    
    @classmethod
    def count(cls, session: Session, **kwargs) -> int:
        return session.scalar(
  select(func.count()).
  select_from({table_name}).filter_by(**kwargs)
)

    @classmethod
    def query_all_by_limit(cls, session: Session, page_number: int, page_size: int, **kwargs) -> List["{table_name}"]:        
        stmt = select(cls).filter_by(**kwargs).offset((page_number - 1) * page_size).limit(page_size)
        return session.exec(stmt).all()
    """

    def __init__(self, has_column_detail=True):
        self.imports = set()
        self.code_indentation = " " * 4
        self.has_column_detail = has_column_detail

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

    def field_details(self, column: Column) -> str:
        """Field repr"""
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
        return " = Field(" + ", ".join(f"{k}={v}" for k, v in kwargs.items()) + ")"

    def _sqlmodel_filed(self, column: Column) -> str:
        _info = (
            f"{self.code_indentation}{column.name}: {column.type.python_type.__name__}"
        )
        if self.has_column_detail:
            _info += self.field_details(column)
        return _info

    @property
    def _model_config_field(self):
        self.imports.add("from pydantic.alias_generators import to_camel")
        self.imports.add("from sqlmodel import SQLModel, Field")
        return (
                self.code_indentation
                + 'model_config = {"alias_generator": to_camel, "populate_by_name": True}'
        )

    def do_field_str(self, table: Table, primary_key_field):
        """do 数据库模型 展示字段"""
        text = [
            f'{self.code_indentation}"""{table.comment or table.description}"""',
            f'{self.code_indentation}__tablename__ = "{table.name}"',
            primary_key_field,
        ]
        return "".join(el + "\n" for el in text)

    def render(self, table: Table):
        """生成model code"""
        table_name = to_pascal(table.name)
        kwargs = {
            "table_name": table_name,
            "primary_key_field": "",
            "fields": "",
            "imports": "",
        }

        for column in table.columns:
            field = self._sqlmodel_filed(column)

            if column.primary_key:
                kwargs["primary_key_field"] = self.do_field_str(table, field)
            else:
                kwargs["fields"] += f"{field}\n"
        kwargs["imports"] = "\n".join(import_str for import_str in self.imports)
        kwargs["model_config"] = 'model_config = {"alias_generator": to_camel, "populate_by_name": True}'

        return self.template.format(**kwargs)
