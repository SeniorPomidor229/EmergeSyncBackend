from bson.objectid import ObjectId
from datetime import datetime
from json import dumps
import asyncio

async def is_jsonable(x):
    try:
        dumps(x)
        return True
    except (TypeError, OverflowError):
        return False

async def get_serialize_document(data) -> dict:
    if isinstance(data, list):
        return await asyncio.gather(*[get_serialize_document(item) for item in data])
    
    if not isinstance(data, dict):
        return str(data)

    buf_data = dict(data)

    for key, value in buf_data.items():
        if not await is_jsonable(value):
            buf_data[key] = str(value)

    return buf_data
