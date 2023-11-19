from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from utils.jwt import decode_token
from data.repository import Repository
from middleware.middleware import oauth2_scheme
from utils.serialize import get_serialize_document

item_router = APIRouter()
repository = Repository("mongodb://admin:T3sT_s3rV@nik.ydns.eu:400/", "EmergeSync")


@item_router.post("/{workflow_id}/")
async def create_workflow_item(workflow_id: str, item: dict, token: str = Depends(oauth2_scheme)):
    credentials = decode_token(token)

    item["workflow_id"] = workflow_id
    result = await repository.insert_one("workflow_items", item)
    log = {
        "workflow_id": workflow_id,
        "user_id": credentials["id"],
        "op": "CREATE",
        "change": result
    }
    await repository.insert_one("workflow_log", log)
    return {"message": "Workflow item created successfully"}

@item_router.get("/{workflow_id}/")
async def get_workflow_items(workflow_id: str, token:str = Depends(oauth2_scheme)):
    # credentials = decode_token(token)
   # projection={"_id":0,"workflow_id":0}
    workflow_items = await repository.find_many("workflow_items", {"workflow_id": workflow_id})
    count = await repository.get_count("workflow_items", {"workflow_id": workflow_id})
    response_data = {
        "Items": await get_serialize_document(workflow_items),
        "Count": count
    }

    return JSONResponse(content=response_data)

@item_router.delete("/{workflow_id}/{item_id}")
async def delete_workflow_item(workflow_id: str, item_id: str, token: str = Depends(oauth2_scheme)):
    credentials = decode_token(token)
    await repository.delete_one("workflow_items", {"_id": item_id, "workflow_id": workflow_id})
    log = {
        "workflow_id": workflow_id,
        "user_id": credentials["id"],
        "op": "DELETE",
        "change": item_id
    }
    await repository.insert_one("workflow_log", log)
    return {"message": "Workflow and item delete successfully"}

@item_router.put("/{workflow_id}/{item_id}")
async def update_workflow_item(workflow_id: str, item_id: str, updated_item: dict, token: str = Depends(oauth2_scheme)):
    credentials = decode_token(token)
    await repository.update_one("workflow_items", {"_id": item_id, "workflow_id": workflow_id}, updated_item)
    log = {
        "workflow_id": workflow_id,
        "user_id": credentials["id"],
        "op": "UPDATE",
        "change": item_id
    }
    await repository.insert_one("workflow_log", log)
    return {"message": "Workflow item updated successfully"}