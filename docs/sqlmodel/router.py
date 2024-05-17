import dao
import schema
from db import engine
from fastapi import APIRouter, Depends
from sqlmodel import Session

aerich = APIRouter(prefix="/Aerich", tags=["Aerich"])


@aerich.get("/{id}", summary="通过ID查询详情")
def query_aerich_by_id(id: int) -> schema.Result[schema.Aerich]:
    with Session(engine) as session:
        return schema.Result.ok(dao.query_by_id(session, id))


@aerich.get("", summary="分页条件查询")
def query_aerich_all_by_limit(query: schema.Aerich = Depends(),
                              page: schema.PageParam = Depends()
                              ) -> schema.PageResult[schema.Aerich]:
    with Session(engine) as session:
        total = dao.count(session, **query.model_dump(exclude_none=True))
        data = dao.query_all_by_limit(session,
                                      **query.model_dump(exclude_none=True),
                                      page_number=page.page_number,
                                      page_size=page.page_size)
        return schema.PageResult.ok(data=data, total=total)


@aerich.post("", summary="新增数据")
def create_aerich(instance: schema.Aerich) -> schema.Result[schema.Aerich]:
    with Session(engine) as session:
        return schema.Result.ok(dao.create(session, instance))


@aerich.patch("/{id}", summary="更新数据")
def update_aerich_by_id(
        id: int, instance: schema.Aerich) -> schema.Result[schema.Aerich]:
    with Session(engine) as session:
        return schema.Result.ok(dao.update(session, id, instance))


@aerich.delete("/{id}", summary="删除数据")
def delete_aerich_by_id(id: int) -> schema.Result[schema.Aerich]:
    with Session(engine) as session:
        return schema.Result.ok(dao.delete_by_id(session, id))
