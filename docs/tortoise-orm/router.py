import dao
import schema
from fastapi import APIRouter, Depends

aerich = APIRouter(prefix="/Aerich", tags=["Aerich"])


@aerich.get("/{id}", summary="通过ID查询详情")
async def query_aerich_by_id(id: int) -> schema.Result[schema.Aerich]:
    return schema.Result.ok(await dao.query_by_id(id))


@aerich.get("", summary="分页条件查询")
async def query_aerich_all_by_limit(query: schema.Aerich = Depends(),
                                    page: schema.PageParam = Depends()
                                    ) -> schema.PageResult[schema.Aerich]:
    total = await dao.count(**query.model_dump(exclude_none=True))
    data = await dao.query_all_by_limit(**query.model_dump(exclude_none=True),
                                        page_number=page.page_number,
                                        page_size=page.page_size)
    return schema.PageResult.ok(data=data, total=total)


@aerich.post("", summary="新增数据")
async def create_aerich(
        instance: schema.Aerich) -> schema.Result[schema.Aerich]:
    return schema.Result.ok(await dao.create(instance))


@aerich.patch("/{id}", summary="更新数据")
async def update_aerich_by_id(
        id: int, instance: schema.Aerich) -> schema.Result[schema.Aerich]:
    return schema.Result.ok(await dao.update(id, instance))


@aerich.delete("/{id}", summary="删除数据")
async def delete_aerich_by_id(id: int) -> schema.Result[schema.Aerich]:
    return schema.Result.ok(await dao.delete_by_id(id))