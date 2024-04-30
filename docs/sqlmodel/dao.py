from typing import List, Optional

import model
import schema
from sqlmodel import Field, Session, SQLModel, func, select


def create(session: Session, obj_in: schema.SysMenu) -> model.SysMenu:
    obj = model.SysMenu(**obj_in.dict())
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


def query_by_id(session: Session, id: int) -> Optional[model.SysMenu]:
    return session.get(model.SysMenu, id)


def update(session: Session, id: int,
           obj_in: schema.SysMenu) -> Optional[model.SysMenu]:
    obj = query_by_id(session, id)
    if obj:
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(obj, field, value)
        session.add(obj)
        session.commit()
        session.refresh(obj)
    return obj


def delete_by_id(session: Session, id: int) -> Optional[model.SysMenu]:
    obj = session.get(model.SysMenu, id)
    if obj:
        session.delete(obj)
        session.commit()
    return obj


def count(session: Session, **kwargs) -> int:
    return session.scalar(
        select(func.count()).select_from(model.SysMenu).filter_by(**kwargs))


def query_all_by_limit(session: Session, page_number: int, page_size: int,
                       **kwargs) -> List[model.SysMenu]:
    stmt = select(model.SysMenu).filter_by(**kwargs).offset(
        (page_number - 1) * page_size).limit(page_size)
    return session.exec(stmt).all()
