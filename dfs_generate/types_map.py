"""
mysql 数据类型映射关系
"""

BOOLEAN = {
    "sqlalchemy": {
        "import": "from sqlalchemy import Boolean",
        "type": "Boolean",
    },
    "tortoise-orm": {
        "import": "from tortoise.fields import BooleanField",
        "type": "BooleanField",
    },
    "pydantic": {
        "import": None,
        "type": "bool",
    },
}

INTEGER = {
    "sqlalchemy": {
        "import": "from sqlalchemy import Integer",
        "type": "Integer",
    },
    "tortoise-orm": {
        "import": "from tortoise.fields import IntField",
        "type": "IntField",
    },
    "pydantic": {
        "import": None,
        "type": "int",
    },
}

VARCHAR = {
    "sqlalchemy": {
        "import": "from sqlalchemy import String",
        "type": "String",
    },
    "tortoise-orm": {
        "import": "from tortoise.fields import CharField",
        "type": "CharField",
    },
    "pydantic": {
        "import": None,
        "type": "str",
    },
}

FLOAT = {
    "sqlalchemy": {
        "import": "from sqlalchemy import Float",
        "type": "Float",
    },
    "tortoise-orm": {
        "import": "from tortoise.fields import FloatField",
        "type": "FloatField",
    },
    "pydantic": {
        "import": None,
        "type": "float",
    },
}

TEXT = {
    "sqlalchemy": {
        "import": "from sqlalchemy import Text",
        "type": "Text",
    },
    "tortoise-orm": {
        "import": "from tortoise.fields import TextField",
        "type": "TextField",
    },
    "pydantic": {
        "import": None,
        "type": "str",
    },
}

BLOB = {
    "sqlalchemy": {
        "import": "from sqlalchemy import LargeBinary",
        "type": "LargeBinary",
    },
    "tortoise-orm": {
        "import": "from tortoise.fields import BinaryField",
        "type": "BinaryField",
    },
    "pydantic": {
        "import": None,
        "type": "bytes",
    },
}

TYPES = {
    "bigint": {
        "sqlalchemy": {
            "import": "from sqlalchemy import BigInteger",
            "type": "BigInteger",
        },
        "tortoise-orm": {
            "import": "from tortoise.fields import IntField",
            "type": "IntField",
        },
        "pydantic": {
            "import": None,
            "type": "int",
        },
    },
    "binary": {
        "sqlalchemy": {
            "import": "from sqlalchemy import Binary",
            "type": "Binary",
        },
        "tortoise-orm": {
            "import": "from tortoise.fields import BinaryField",
            "type": "BinaryField",
        },
        "pydantic": {
            "import": None,
            "type": "bytes",
        },
    },
    "bit": BOOLEAN,
    "blob": BLOB,
    "bool": BOOLEAN,
    "boolean": BOOLEAN,
    "char": VARCHAR,
    "date": {
        "sqlalchemy": {
            "import": "from sqlalchemy import Date",
            "type": "Date",
        },
        "tortoise-orm": {
            "import": "from tortoise.fields import DateField",
            "type": "DateField",
        },
        "pydantic": {
            "import": "from datetime import date",
            "type": "date",
        },
    },
    "datetime": {
        "sqlalchemy": {
            "import": "from sqlalchemy import DateTime",
            "type": "DateTime",
        },
        "tortoise-orm": {
            "import": "from tortoise.fields import DatetimeField",
            "type": "DatetimeField",
        },
        "pydantic": {
            "import": "from datetime import datetime",
            "type": "datetime",
        },
    },
    "decimal": {
        "sqlalchemy": {
            "import": "from sqlalchemy import DECIMAL",
            "type": "DECIMAL",
        },
        "tortoise-orm": {
            "import": "from tortoise.fields import DecimalField",
            "type": "DecimalField",
        },
        "pydantic": {
            "import": "from decimal import Decimal",
            "type": "Decimal",
        },
    },
    "double": FLOAT,
    "enum": {
        "sqlalchemy": {
            "import": "from sqlalchemy import Enum",
            "type": "Enum",
        },
        "tortoise-orm": {
            "import": "from tortoise.fields import CharEnumField",
            "type": "CharEnumField",
        },
        "pydantic": {
            "import": "from enum import Enum",
            "type": "Enum",
        },
    },
    "float": FLOAT,
    "int": INTEGER,
    "integer": INTEGER,
    "json": {
        "sqlalchemy": {
            "import": "from sqlalchemy import JSON",
            "type": "JSON",
        },
        "tortoise-orm": {
            "import": "from tortoise.fields import JSONField",
            "type": "JSONField",
        },
        "pydantic": {
            "import": None,
            "type": "dict",
        },
    },
    "longblob": BLOB,
    "longtext": TEXT,
    "mediumblob": BLOB,
    "mediumint": INTEGER,
    "mediumtext": TEXT,
    "set": {
        "sqlalchemy": {
            "import": "from sqlalchemy import String",
            "type": "String",
        },
        "tortoise-orm": {
            "import": "from tortoise.fields import CharEnumField",
            "type": "CharEnumField",
        },
        "pydantic": {
            "import": "from typing import List",
            "type": "List[str]",
        },
    },
    "smallint": {
        "sqlalchemy": {
            "import": "from sqlalchemy import SmallInteger",
            "type": "SmallInteger",
        },
        "tortoise-orm": {
            "import": "from tortoise.fields import SmallIntField",
            "type": "SmallIntField",
        },
        "pydantic": {
            "import": None,
            "type": "int",
        },
    },
    "text": TEXT,
    "time": {
        "sqlalchemy": {
            "import": "from sqlalchemy import Time",
            "type": "Time",
        },
        "tortoise-orm": {
            "import": "from tortoise.fields import TimeField",
            "type": "TimeField",
        },
        "pydantic": {
            "import": "from datetime import time",
            "type": "time",
        },
    },
    "timestamp": {
        "sqlalchemy": {
            "import": "from sqlalchemy import TIMESTAMP",
            "type": "TIMESTAMP",
        },
        "tortoise-orm": {
            "import": "from tortoise.fields import DatetimeField",
            "type": "DatetimeField",
        },
        "pydantic": {
            "import": "from datetime import datetime",
            "type": "datetime",
        },
    },
    "tinyblob": BLOB,
    "tinyint": INTEGER,
    "tinytext": TEXT,
    "varbinary": BLOB,
    "varchar": VARCHAR,
    "year": {
        "sqlalchemy": {
            "import": "from sqlalchemy import SmallInteger",
            "type": "SmallInteger",
        },
        "tortoise-orm": {
            "import": "from tortoise.fields import SmallIntField",
            "type": "SmallIntField",
        },
        "pydantic": {
            "import": None,
            "type": "int",
        },
    },
    # other
    "geometry": VARCHAR,  # Serialize as WKT or WKB string
    "point": VARCHAR,  # Serialize as WKT or WKB string
    "linestring": VARCHAR,  # Serialize as WKT or WKB string
    "polygon": VARCHAR,  # Serialize as WKT or WKB string
    "multipoint": VARCHAR,  # Serialize as WKT or WKB string
    "multilinestring": VARCHAR,  # Serialize as WKT or WKB string
    "multipolygon": VARCHAR,  # Serialize as WKT or WKB string
    "geometrycollection": VARCHAR,
}
