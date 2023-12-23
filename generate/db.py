template = """
from sqlmodel import create_engine, MetaData

db_uri = "{db_uri}"

engine = create_engine(db_uri)
"""


def render(db_uri):
    """数据库链接- sqlalchemy"""
    return template.format(db_uri=db_uri)
