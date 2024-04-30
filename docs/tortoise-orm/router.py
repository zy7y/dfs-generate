import dao
import schema
from fastapi import APIRouter, Depends

sys_menu = APIRouter(prefix="/SysMenu", tags=["SysMenu"])


@sys_menu.get("/{id}", summary="通过ID查询详情")
async def query_sys_menu_by_id(id: int) -> schema.Result[schema.SysMenu]:
    return schema.Result.ok(await dao.query_by_id(id))


@sys_menu.get("", summary="分页条件查询")
async def query_sys_menu_all_by_limit(query: schema.SysMenu = Depends(),
                                      page: schema.PageParam = Depends()
                                      ) -> schema.PageResult[schema.SysMenu]:
    total = await dao.count(**query.model_dump(exclude_none=True))
    data = await dao.query_all_by_limit(**query.model_dump(exclude_none=True),
                                        page_number=page.page_number,
                                        page_size=page.page_size)
    return schema.PageResult.ok(data=data, total=total)


@sys_menu.post("", summary="新增数据")
async def create_sys_menu(
        instance: schema.SysMenu) -> schema.Result[schema.SysMenu]:
    return schema.Result.ok(await dao.create(instance))


@sys_menu.patch("/{id}", summary="更新数据")
async def update_sys_menu_by_id(
        id: int, instance: schema.SysMenu) -> schema.Result[schema.SysMenu]:
    return schema.Result.ok(await dao.update(id, instance))


@sys_menu.delete("/{id}", summary="删除数据")
async def delete_sys_menu_by_id(id: int) -> schema.Result[schema.SysMenu]:
    return schema.Result.ok(await dao.delete_by_id(id))
