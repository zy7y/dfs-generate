imports = {
    "from typing import Generic, List, Optional",
    "from sqlmodel import Session, SQLModel,select",
}

template = """
    @classmethod
    def create(cls, session: Session, obj_in: {table_name}DO) -> "{table_name}":
        obj = cls(**obj_in.dict())
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    @classmethod
    def get_by_id(cls, session: Session, id: int) -> Optional["{table_name}"]:
        return session.get(cls, id)

    @classmethod
    def update(cls, session: Session, id: int, obj_in: {table_name}DO) -> Optional["{table_name}"]:
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
    def find_with_pagination(cls, session: Session, page: int, page_size: int, **kwargs) -> List["{table_name}"]:
        stmt = select(cls).where(**kwargs).offset((page - 1) * page_size).limit(page_size)
        return session.exec(stmt).all()
"""
