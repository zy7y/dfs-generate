imports = {
    "from typing import List, Optional",
    "from sqlmodel import Session, SQLModel,select, func",
}

template = """
    @classmethod
    def create(cls, session: Session, obj_in: {table_name}DTO) -> "{table_name}":
        obj = cls(**obj_in.dict())
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    @classmethod
    def get_by_id(cls, session: Session, id: int) -> Optional["{table_name}"]:
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
    def count(cls, session: Session, **kwargs):
        return session.scalar(
  select(func.count()).
  select_from({table_name}).filter_by(**kwargs)
)

    @classmethod
    def query_all_by_limit(cls, session: Session, page_number: int, page_size: int, **kwargs):        
        stmt = select(cls).filter_by(**kwargs).offset((page_number - 1) * page_size).limit(page_size)
        return dict(data=session.exec(stmt).all(), total=cls.count(session, kwargs))
"""
