from typing import List, Optional

import model
import schema


async def create(obj_in: schema.SysMenu) -> model.SysMenu:
    obj = model.SysMenu(**obj_in.dict())
    await obj.save()
    return obj


async def query_by_id(id: int) -> Optional[model.SysMenu]:
    return await model.SysMenu.get_or_none(id=id)


async def update(id: int, obj_in: schema.SysMenu) -> Optional[model.SysMenu]:
    obj = await query_by_id(id)
    if obj:
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(obj, field, value)
        await obj.save()
    return obj


async def delete_by_id(id: int) -> Optional[model.SysMenu]:
    obj = await query_by_id(id)
    if obj:
        await obj.delete()
    return obj


async def count(**kwargs) -> int:
    return await model.SysMenu.filter(**kwargs).count()


async def query_all_by_limit(page_number: int, page_size: int,
                             **kwargs) -> List[model.SysMenu]:
    offset = (page_number - 1) * page_size
    limit = page_size
    return await model.SysMenu.filter(**kwargs
                                      ).offset(offset).limit(limit).all()
