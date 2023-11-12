from fastapi import APIRouter, HTTPException, Depends, UploadFile, File   
from data.repository import Repository
from utils.jwt import decode_token
from middleware.middleware import oauth2_scheme
from datetime import datetime
from pydantic import BaseModel
import pandas as pd 

workflow_router = APIRouter()
repository = Repository(
    "mongodb://admin:T3sT_s3rV@nik.ydns.eu:400/", 
    "EmergeSync")

class Workflow(BaseModel):
    name: str
    create_at: datetime
    last_modify: datetime

@workflow_router.post("/")
async def create_workflow(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    credentials = decode_token(token)
    try:
        df = pd.read_excel(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading Excel file: {str(e)}")

    workflow_data = {
        "name": "", 
        "create_at": datetime.utcnow(),
        "last_modify": datetime.utcnow(),
        "user_id": credentials["id"]
    }
    workflow_id = await repository.insert_one("workflows", workflow_data)
    for _, row in df.iterrows():
        workflow_item_data = {
            "workflow_id": workflow_id,
            "column1": row["column1"],  
            "column2": row["column2"],
        }
        await repository.insert_one("workflow_items", workflow_item_data)

    return {"message": "Workflow and workflow items created successfully"}

@workflow_router.get("/")
async def get_workflows(token: str = Depends(oauth2_scheme)):
    credentials = decode_token(token)

    workflows = await repository.find("workflows", {"user_id": credentials["id"]})
    return workflows
