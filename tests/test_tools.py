import pymysql
import pytest
from dfs_generate.tools import tran, to_pascal, to_snake
from dfs_generate.tools import MySQLConf, MySQLHelper
from unittest.mock import MagicMock
from pymysql.err import OperationalError


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
    assert tran(t, mode) == expected


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
        conf.get_db_uri()
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


@pytest.fixture
def mysql_helper_mock(monkeypatch):
    """Fixture to create a mocked MySQLHelper instance."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr("pymysql.connect", lambda *args, **kwargs: mock_conn)
    helper = MySQLHelper(
        MySQLConf(host="localhost", user="test", password="pwd", db="test_db")
    )
    return helper, mock_conn, mock_cursor


def test_mysqlhelper_init(mysql_helper_mock):
    helper, mock_conn, _ = mysql_helper_mock
    mock_conn.assert_called_once()
    assert helper.conn == mock_conn
    assert helper.cursor == mock_conn.cursor.return_value


def test_mysqlhelper_set_conn(mysql_helper_mock):
    helper, mock_conn, _ = mysql_helper_mock
    new_conf = MySQLConf(
        host="new_host", user="new_user", password="new_pwd", db="new_db"
    )
    helper.set_conn(new_conf)
    mock_conn.assert_called_with(
        **new_conf.json(), cursorclass=pymysql.cursors.DictCursor
    )


def test_mysqlhelper_close(mysql_helper_mock):
    _, mock_conn, mock_cursor = mysql_helper_mock
    helper = MySQLHelper(
        MySQLConf(host="localhost", user="test", password="pwd", db="test_db")
    )
    helper.close()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


def test_mysqlhelper_get_tables_error(mysql_helper_mock):
    helper, _, mock_cursor = mysql_helper_mock
    mock_cursor.execute.side_effect = OperationalError
    with pytest.raises(OperationalError):
        helper.get_tables()
