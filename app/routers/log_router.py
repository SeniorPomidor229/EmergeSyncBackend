from fastapi import APIRouter, HTTPException, Depends, UploadFile, File   
from data.repository import Repository
from utils.jwt import decode_token
from middleware.middleware import oauth2_scheme
from datetime import datetime
from pydantic import BaseModel
from utils.serialize import get_serialize_document
import pandas as pd 
import logging

workflow_router = APIRouter()
repository = Repository(
    "mongodb://admin:T3sT_s3rV@nik.ydns.eu:400/", 
    "EmergeSync")

logger = logging.getLogger(__name__)

class Workflow(BaseModel):
    name: str
    create_at: datetime
    last_modify: datetime

@workflow_router.post("/")
async def create_workflow(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    credentials = decode_token(token)
    logger.info(f"User {credentials['username']} is creating a workflow.")

    df = pd.read_excel(file.file)
    
    workflow_data = {
        "name": f"{file.filename}",
        "create_at": datetime.utcnow(),
        "last_modify": datetime.utcnow(),
        "user_id": credentials["id"]
    }
    workflow_id = await repository.insert_one("workflows", workflow_data)

    workflow_items_list = df.to_dict(orient="records")

    for item in workflow_items_list:
        item["workflow_id"] = str(workflow_id)

    await repository.insert_many("workflow_items", workflow_items_list)

    return {"message": "Workflow and workflow items created successfully"}

@workflow_router.get("/")
async def get_workflows(token: str = Depends(oauth2_scheme)):
    credentials = decode_token(token)
    logger.info(f"User {credentials['username']} is retrieving workflows.")

    workflows = await repository.find_many("workflows", {"user_id": credentials["id"]})
    return get_serialize_document(workflows)

@workflow_router.delete("/{id}")
async def del_worflow(id: str, token: str = Depends(oauth2_scheme)):
    credentials = decode_token(token)
    logger.info(f"User {credentials['username']} is deleting workflow with id {id}.")

    await repository.delete_by_id("workflows", id)
    await repository.delete_many("workflow_items", {"workflow_id": id})
    return {"message": "Workflow and items deleted successfully"}
