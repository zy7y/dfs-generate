from typing import List, Optional

import model
import schema


async def create(obj_in: schema.Aerich) -> model.Aerich:
    obj = model.Aerich(**obj_in.model_dump(exclude_unset=True))
    await obj.save()
    return obj


async def query_by_id(id: int) -> Optional[model.Aerich]:
    return await model.Aerich.get_or_none(aerich_id=id)


async def update(id: int, obj_in: schema.Aerich) -> Optional[model.Aerich]:
    obj = await query_by_id(id)
    if obj:
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        await obj.save()
    return obj


async def delete_by_id(id: int) -> Optional[model.Aerich]:
    obj = await query_by_id(id)
    if obj:
        await obj.delete()
    return obj


async def count(**kwargs) -> int:
    return await model.Aerich.filter(**kwargs).count()


async def query_all_by_limit(page_number: int, page_size: int,
                             **kwargs) -> List[model.Aerich]:
    offset = (page_number - 1) * page_size
    limit = page_size
    return await model.Aerich.filter(**kwargs
                                     ).offset(offset).limit(limit).all()