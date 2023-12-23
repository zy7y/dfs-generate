from sqlmodel import Field, MetaData, Session, SQLModel, create_engine, select

db_uri = "sqlite:///dfs-generate.sqlite"
engine = create_engine(db_uri)
metadata = MetaData()
metadata.reflect(bind=engine)


class Conf(SQLModel, table=True):
    __tablename__ = "dfs_generate_conf"
    id: int = Field(None, primary_key=True)
    db_uri: str = Field(..., description="数据库连接")

    @classmethod
    def get_db_uri_last_new(cls):
        """获取最新的db_url"""
        with Session(engine) as session:
            query = select(cls).order_by(cls.id.desc())
            latest_conf = session.exec(query).first()
            if latest_conf:
                return latest_conf.db_uri
            else:
                return None

    @classmethod
    def create(cls, uri) -> "Conf":
        with Session(engine) as session:
            obj = cls(db_uri=uri)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj


def get_db_uri(user, password, host, port, db):
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"


def get_metadata_by_db_uri(uri: str):
    db_engine = create_engine(uri)
    db_metadata = MetaData()
    db_metadata.reflect(bind=db_engine)
    return db_metadata
