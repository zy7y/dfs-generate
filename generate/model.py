from typing import Any, Dict, Sequence

from pydantic.alias_generators import to_pascal
from sqlmodel import DATETIME, Column, Table


class GenerateEntity:
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

class {table_name}DTO(SQLModel):
{dto_fields}
class {table_name}Query({table_name}DTO):
    page_number: int = Field(1, description="页码")
    page_size: int = Field(10, description="页量")
{query_fields}
    
    def count_kwargs(self, **kwargs):
        default_exclude = {default_exclude}
        if v := kwargs.get("exclude"):
            default_exclude.union(v)
        data = self.model_dump(exclude=default_exclude, **kwargs)
        return data

class {table_name}({table_name}DTO, table=True):\n{do_fields}\n
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
        obj = cls.query_by_id(session, id)
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

    def __init__(self, table: Table):
        self.table = table
        self.do_fields = []
        self.dto_fields = []
        self.query_fields = []
        self.imports = set()
        self.indent = " " * 4

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

    def render(self) -> str:
        """生成model code"""
        self.add_dto_head_field()
        for column in self.table.columns:
            self.add_field_by_column(column)
        self.add_do_tail_field()
        kwargs = {
            "table_name": to_pascal(self.table.name),
            "imports": self.render_fields_str(self.imports, use_indent=False),
            "dto_fields": self.render_fields_str(self.dto_fields),
            "do_fields": self.render_fields_str(self.do_fields),
            "query_fields": self.render_fields_str(self.query_fields),
            "default_exclude": "{'page_number', 'page_size'}",
        }

        return self.template.format(**kwargs)
