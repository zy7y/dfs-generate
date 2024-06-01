import pytest
from dfs_generate.tools import tran, to_pascal, to_snake
from dfs_generate.tools import MySQLConf


# 测试 tran 函数
@pytest.mark.parametrize(
    "t, mode, expected",
    [
        ("int", "sqlalchemy", {"type": "Integer"}),
        ("varchar", "tortoise-orm", {"type": "CharField"}),
        ("bool", "pydantic", {"type": "bool"}),
    ],
)
def test_tran(t, mode, expected):
    assert tran(t, mode)["type"] == expected["type"]


# 测试 to_pascal 函数
@pytest.mark.parametrize(
    "snake, expected",
    [
        ("hello_world", "HelloWorld"),
        ("user_id", "UserId"),
        ("some_value", "SomeValue"),
    ],
)
def test_to_pascal(snake, expected):
    assert to_pascal(snake) == expected


# 测试 to_snake 函数
@pytest.mark.parametrize(
    "camel, expected",
    [
        ("helloWorld", "hello_world"),
        ("userId", "user_id"),
        ("someValue", "some_value"),
        ("HTTPRequest", "http_request"),
        ("123abc", "123abc"),  # No change for non-camelCase inputs
    ],
)
def test_to_snake(camel, expected):
    assert to_snake(camel) == expected


def test_mysqlconf_get_db_uri():
    conf = MySQLConf(
        host="localhost", user="test_user", password="secure_pwd", db="test_db"
    )
    assert (
        conf.db_uri
        == "mysql+pymysql://test_user:secure_pwd@localhost:3306/test_db?charset=utf8"
    )


def test_mysqlconf_json():
    conf = MySQLConf(
        host="localhost",
        user="test_user",
        password="pwd",
        db="test_db",
        port=3307,
        charset="utf8mb4",
    )
    expected_json = {
        "host": "localhost",
        "user": "test_user",
        "password": "pwd",
        "db": "test_db",
        "port": 3307,
        "charset": "utf8mb4",
    }
    assert conf.json() == expected_json
