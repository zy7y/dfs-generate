import pytest
from dfs_generate.conversion import (
    Conversion,
    SQLModelConversion,
    TortoiseConversion,
    _pydantic_field,
    _sqlmodel_field_repr,
    _tortoise_field_repr,
    _fast_crud_column,
    _antd_crud_column
)

# 假设的列数据，用于模拟从数据库获取的信息
MOCK_COLUMNS = [
    {
        "COLUMN_NAME": "id",
        "DATA_TYPE": "int",
        "IS_NULLABLE": "NO",
        "COLUMN_KEY": "PRI",
        "COLUMN_COMMENT": "主键ID",
        "CHARACTER_MAXIMUM_LENGTH": "",
        "NUMERIC_PRECISION": "",
        "NUMERIC_SCALE": "",
        "COLUMN_DEFAULT": "",
        "EXTRA": "",
    },
    {
        "COLUMN_NAME": "name",
        "DATA_TYPE": "varchar",
        "IS_NULLABLE": "YES",
        "COLUMN_COMMENT": "姓名",
        "CHARACTER_MAXIMUM_LENGTH": "100",
        "NUMERIC_PRECISION": "",
        "NUMERIC_SCALE": "",
        "COLUMN_DEFAULT": "",
        "EXTRA": "",
        "COLUMN_KEY": "",
    },
]

# 假定的table_name和uri
MOCK_TABLE_NAME = "users"
MOCK_URI = "mysql+pymysql://user:pass@localhost/dbname"


@pytest.fixture
def conversion_fixture():
    return Conversion(MOCK_TABLE_NAME, MOCK_COLUMNS, MOCK_URI)


@pytest.fixture
def sqlmodel_conversion_fixture():
    return SQLModelConversion(MOCK_TABLE_NAME, MOCK_COLUMNS, MOCK_URI)


@pytest.fixture
def tortoise_conversion_fixture():
    return TortoiseConversion(MOCK_TABLE_NAME, MOCK_COLUMNS, MOCK_URI)


def test_conversion_initialization(conversion_fixture):
    """测试Conversion类的初始化"""
    assert conversion_fixture.table_name == MOCK_TABLE_NAME
    assert conversion_fixture.router_name == "users"


def test_sqlmodel_conversion_model(sqlmodel_conversion_fixture):
    """测试SQLModelConversion的model方法输出格式"""
    # 这里简化测试，只检查输出是否包含一些预期的关键字
    model_code = sqlmodel_conversion_fixture.model()
    assert "class Users(SQLModel, table=True):" in model_code
    assert "id: Optional[int] =" in model_code
    assert "name: Optional[str] =" in model_code


def test_tortoise_conversion_model(tortoise_conversion_fixture):
    """测试TortoiseConversion的model方法输出格式"""
    model_code = tortoise_conversion_fixture.model()
    assert "class Users(Model):" in model_code
    assert 'id = fields.IntField(description="主键ID", pk=True)' in model_code
    assert (
            'name = fields.CharField(null=True, max_length=100, description="姓名")'
            in model_code
    )


def test_pydantic_field():
    """测试_pydantic_field函数的输出"""
    column = MOCK_COLUMNS[1]  # 使用name字段作为测试
    field_code = _pydantic_field(column, set())
    assert "name: Optional[str] = Field(None, description='姓名')" in field_code


def test_sqlmodel_field_repr():
    """测试_sqlmodel_field_repr函数的输出"""
    column = MOCK_COLUMNS[0]  # 使用id字段作为测试
    imports, field_code = set(), _sqlmodel_field_repr(column, set())
    assert (
            'id: Optional[int] = Field(default=None,primary_key=True,description="主键ID")'
            == field_code
    )
    assert (
            "from datetime import datetime" not in imports
    )  # id字段不应触发默认时间戳逻辑


def test_tortoise_field_repr():
    """测试_tortoise_field_repr函数的输出"""
    column = MOCK_COLUMNS[1]
    field_code = _tortoise_field_repr(column)
    assert (
            'name = fields.CharField(null=True, max_length=100, description="姓名")'
            == field_code
    )


@pytest.mark.parametrize("column_data,expected", [
    ({"COLUMN_NAME": "user_name", "COLUMN_COMMENT": "User's Name"},
     "userName: { title: 'User's Name', type: 'text', search: { show: true }}"),
    ({"COLUMN_NAME": "is_active", "COLUMN_COMMENT": ""},
     "isActive: { title: 'isActive', type: 'text', search: { show: true }}"),
    ({"COLUMN_NAME": "last_login_dt", "COLUMN_COMMENT": "Last Login Date & Time"},
     "lastLoginDt: { title: 'Last Login Date & Time', type: 'text', search: { show: true }}"),
])
def test_fast_crud_column(column_data, expected):
    assert _fast_crud_column(column_data) == expected


@pytest.mark.parametrize("column_data,expected", [
    ({"COLUMN_NAME": "user_name", "COLUMN_COMMENT": "User's Name"},
     "{ title: 'User's Name', dataIndex: 'userName', key: 'userName', supportSearch: true}"),
    ({"COLUMN_NAME": "is_active", "COLUMN_COMMENT": ""},
     "{ title: 'isActive', dataIndex: 'isActive', key: 'isActive', supportSearch: true}"),
    ({"COLUMN_NAME": "last_login_dt", "COLUMN_COMMENT": "Last Login Date & Time"},
     "{ title: 'Last Login Date & Time', dataIndex: 'lastLoginDt', key: 'lastLoginDt', supportSearch: true}"),
])
def test_antd_crud_column(column_data, expected):
    assert _antd_crud_column(column_data) == expected
