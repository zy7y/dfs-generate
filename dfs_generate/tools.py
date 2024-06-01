import os
import re
import sqlite3
import threading
from dataclasses import asdict, dataclass

import pymysql

from dfs_generate.types_map import TYPES


def tran(t, mode) -> dict:
    """
    转换获取对应mode下的导包和类型
    :params  t  mysql 列数据类型名称
    :params model 模式
    """
    assert mode in ["sqlalchemy", "tortoise-orm", "pydantic"], "暂不支持其他模式"
    assert t in TYPES, f"暂不支持{t}类型"
    return TYPES[t][mode]


def to_pascal(snake: str) -> str:
    """Convert a snake_case string to PascalCase.

    Args:
        snake: The string to convert.

    Returns:
        The PascalCase string.
    """
    camel = snake.title()
    return re.sub("([0-9A-Za-z])_(?=[0-9A-Z])", lambda m: m.group(1), camel)


def to_snake(camel: str) -> str:
    """Convert a PascalCase or camelCase string to snake_case.

    Args:
        camel: The string to convert.

    Returns:
        The converted string in snake_case.
    """
    # Handle the sequence of uppercase letters followed by a lowercase letter
    snake = re.sub(
        r"([A-Z]+)([A-Z][a-z])", lambda m: f"{m.group(1)}_{m.group(2)}", camel
    )
    # Insert an underscore between a lowercase letter and an uppercase letter
    snake = re.sub(r"([a-z])([A-Z])", lambda m: f"{m.group(1)}_{m.group(2)}", snake)
    # Insert an underscore between a digit and an uppercase letter
    snake = re.sub(r"([0-9])([A-Z])", lambda m: f"{m.group(1)}_{m.group(2)}", snake)
    # Insert an underscore between a lowercase letter and a digit
    snake = re.sub(r"([a-z])([0-9])", lambda m: f"{m.group(1)}_{m.group(2)}", snake)
    return snake.lower()


def to_camel(snake: str) -> str:
    """Convert a snake_case string to camelCase.

    Args:
        snake: The string to convert.

    Returns:
        The converted camelCase string.
    """
    camel = to_pascal(snake)
    return re.sub("(^_*[A-Z])", lambda m: m.group(1).lower(), camel)


@dataclass
class MySQLConf:
    host: str
    user: str
    password: str
    db: str
    port: int = 3306
    charset: str = "utf8"

    @property
    def db_uri(self):
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}?charset={self.charset}"

    def json(self):
        return asdict(self)


class MySQLHelper:
    """引用 https://github.com/tortoise/aerich/blob/dev/aerich/inspectdb/mysql.py"""

    GET_TABLES = (
        "select TABLE_NAME from information_schema.TABLES where TABLE_SCHEMA=%s"
    )
    GET_TABLE_COLUMNS = """select c.*, s.NON_UNIQUE, s.INDEX_NAME
from information_schema.COLUMNS c
         left join information_schema.STATISTICS s on c.TABLE_NAME = s.TABLE_NAME
    and c.TABLE_SCHEMA = s.TABLE_SCHEMA
    and c.COLUMN_NAME = s.COLUMN_NAME
where c.TABLE_SCHEMA = %s
  and c.TABLE_NAME = %s"""

    def __init__(self, conf: MySQLConf):
        self.conf = conf
        self.conn = pymysql.connect(
            **self.conf.json(), cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def get_tables(self):
        """获取所有表"""
        self.cursor.execute(self.GET_TABLES, [self.conf.db])
        tables = self.cursor.fetchall()
        return [table["TABLE_NAME"] for table in tables]

    def get_table_columns(self, table_name):
        """获取表所有字段"""
        self.cursor.execute(self.GET_TABLE_COLUMNS, [self.conf.db, table_name])
        rows = self.cursor.fetchall()
        return sorted(rows, key=lambda x: x["ORDINAL_POSITION"])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def get_cache_directory():
    """
    获取适用于不同操作系统的缓存目录路径。
    """
    system = os.name
    if system == "posix":  # Linux, macOS, Unix
        return os.path.expanduser("~/.cache")
    elif system == "nt":  # Windows
        return os.path.expandvars(r"%LOCALAPPDATA%")
    else:
        return "."  # 不支持的操作系统


class Cache:
    def __init__(self):
        self.db_path = os.path.join(get_cache_directory(), "dfs-generate", ".data.db")
        self._local = threading.local()  # 使用线程局部存储

    def _get_connection(self):
        if not hasattr(self._local, "conn"):
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self._local.conn

    def _close_connection(self):
        if hasattr(self._local, "conn"):
            self._local.conn.close()
            del self._local.conn

    def start(self):
        if not os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            create_table_sql = """
                CREATE TABLE IF NOT EXISTS conf (
                    id INTEGER PRIMARY KEY,
                    user TEXT NOT NULL,
                    password TEXT NOT NULL,
                    host TEXT NOT NULL,
                    port INT NOT NULL,
                    db TEXT NOT NULL,
                    charset TEXT NOT NULL
                );
            """
            cursor.execute(create_table_sql)
            conn.commit()
            conn.close()

    def set(self, user, password, host, port, db, charset):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            insert_sql = """
                INSERT INTO conf (user, password, host, port, db, charset) VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_sql, (user, password, host, port, db, charset))
            conn.commit()

    def get(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query_sql = """
                SELECT user, password, host, port, db, charset FROM conf ORDER BY id DESC LIMIT 1
            """
            cursor.execute(query_sql)
            result = cursor.fetchone()
            if result:
                keys = ["user", "password", "host", "port", "db", "charset"]
                return dict(zip(keys, result))
            return None

    def cleanup(self):
        self._close_connection()
