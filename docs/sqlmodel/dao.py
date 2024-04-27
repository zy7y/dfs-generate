from typing import List, Optional

import model
import schema
from sqlmodel import Session, func, select


def create(session: Session, obj_in: schema.Aerich) -> model.Aerich:
    obj = model.Aerich(**obj_in.dict())
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


def query_by_id(session: Session, id: int) -> Optional[model.Aerich]:
    return session.get(model.Aerich, id)


def update(session: Session, id: int, obj_in: schema.Aerich) -> Optional[model.Aerich]:
    obj = query_by_id(session, id)
    if obj:
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(obj, field, value)
        session.add(obj)
        session.commit()
        session.refresh(obj)
    return obj


def delete_by_id(session: Session, id: int) -> Optional[model.Aerich]:
    obj = session.get(model.Aerich, id)
    if obj:
        session.delete(obj)
        session.commit()
    return obj


def count(session: Session, **kwargs) -> int:
    return session.scalar(
        select(func.count()).select_from(model.Aerich).filter_by(**kwargs)
    )


def query_all_by_limit(
    session: Session, page_number: int, page_size: int, **kwargs
) -> List[model.Aerich]:
    stmt = (
        select(model.Aerich)
        .filter_by(**kwargs)
        .offset((page_number - 1) * page_size)
        .limit(page_size)
    )
    return session.exec(stmt).all()
