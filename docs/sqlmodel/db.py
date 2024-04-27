from sqlmodel import create_engine

db_uri = "mysql+pymysql://root:123456@127.0.0.1:3306/mini-rbac?charset=utf8"

engine = create_engine(db_uri)
