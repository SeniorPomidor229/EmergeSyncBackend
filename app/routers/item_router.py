from fastapi import APIRouter, Depends, HTTPException
from utils.jwt import decode_token
from data.repository import Repository
from middleware.middleware import oauth2_scheme
from pydantic import BaseModel
from datetime import datetime
from utils.serialize import get_serialize_document

item_router = APIRouter()
repository = Repository("mongodb://admin:T3sT_s3rV@nik.ydns.eu:400/", "EmergeSync")


@item_router.post("/{workflow_id}/")
async def create_workflow_item(workflow_id: str, item: dict, token: str = Depends(oauth2_scheme)):
    credentials = decode_token(token)

    item["workflow_id"] = workflow_id
    await repository.insert_one("workflow_items", item)

    return {"message": "Workflow item created successfully"}


@item_router.get("/workflow/{workflow_id}/items/")
async def get_workflow_items(workflow_id: str, token: str = Depends(oauth2_scheme)):
    credentials = decode_token(token)
    workflow_items = await repository.find_many("workflow_items", {"workflow_id": workflow_id})
    return get_serialize_document(workflow_items)

@item_router.delete("/{workflow_id}/{item_id}")
async def delete_workflow_item(workflow_id: str, item_id: str, token: str = Depends(oauth2_scheme)):
    credentials = decode_token(token)
    await repository.delete_one("workflow_items", {"_id": item_id, "workflow_id": workflow_id, "user_id": credentials["id"]})
    return {"message": "Workflow and item delete successfully"}
