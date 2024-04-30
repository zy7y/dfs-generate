import dao
import schema
from db import engine
from fastapi import APIRouter, Depends
from sqlmodel import Session

sys_menu = APIRouter(prefix="/SysMenu", tags=["SysMenu"])


@sys_menu.get("/{id}", summary="通过ID查询详情")
def query_sys_menu_by_id(id: int) -> schema.Result[schema.SysMenu]:
    with Session(engine) as session:
        return schema.Result.ok(dao.query_by_id(session, id))


@sys_menu.get("", summary="分页条件查询")
def query_sys_menu_all_by_limit(query: schema.SysMenu = Depends(),
                                page: schema.PageParam = Depends()
                                ) -> schema.PageResult[schema.SysMenu]:
    with Session(engine) as session:
        total = dao.count(session, **query.model_dump(exclude_none=True))
        data = dao.query_all_by_limit(session,
                                      **query.model_dump(exclude_none=True),
                                      page_number=page.page_number,
                                      page_size=page.page_size)
        return schema.PageResult.ok(data=data, total=total)


@sys_menu.post("", summary="新增数据")
def create_sys_menu(instance: schema.SysMenu) -> schema.Result[schema.SysMenu]:
    with Session(engine) as session:
        return schema.Result.ok(dao.create(session, instance))


@sys_menu.patch("/{id}", summary="更新数据")
def update_sys_menu_by_id(
        id: int, instance: schema.SysMenu) -> schema.Result[schema.SysMenu]:
    with Session(engine) as session:
        return schema.Result.ok(dao.update(session, id, instance))


@sys_menu.delete("/{id}", summary="删除数据")
def delete_sys_menu_by_id(id: int) -> schema.Result[schema.SysMenu]:
    with Session(engine) as session:
        return schema.Result.ok(dao.delete_by_id(session, id))
