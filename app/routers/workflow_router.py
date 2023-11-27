from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from bson import ObjectId
from data.repository import Repository
from utils.jwt import decode_token
from middleware.middleware import oauth2_scheme
from datetime import datetime
from pydantic import BaseModel
from utils.serialize import get_serialize_document
import pandas as pd
from fastapi.responses import JSONResponse
workflow_router = APIRouter()
repository = Repository(
    "mongodb://admin:T3sT_s3rV@nik.ydns.eu:400/",
    "EmergeSync"
)


class Workflow(BaseModel):
    name: str
    create_at: datetime
    last_modify: datetime


@workflow_router.post("/")
async def create_workflow(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    try:
        credentials = decode_token(token)
        print(file.file)

        df = pd.read_excel(file.file)
        df.fillna('', inplace=True)
        users=[]
        workflow_data = {
            "name": f"{file.filename}",  # название файла
            "create_at": datetime.utcnow(),
            "last_modify": datetime.utcnow(),
            "creater_id":credentials["id"],
            "user_id": users.append(credentials["id"])
        }
        workflow_id = await repository.insert_one("workflows", workflow_data)

        workflow_items_list = [{str(key): value for key, value in item.items()}
                               for item in df.to_dict(orient="records")]

        for item in workflow_items_list:
            item["workflow_id"] = str(workflow_id)

        await repository.insert_many("workflow_items", workflow_items_list)
        response_data = {"workflow_id": str(workflow_id)}
        return JSONResponse(content=response_data)
        # return {"message": "Workflow and workflow items created successfully"}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@workflow_router.get("/")
async def get_workflows(token: str = Depends(oauth2_scheme)):
    try:
        credentials = decode_token(token)
        workflows = await repository.find_many("workflows",{"user_id": {"$in": [credentials["id"]]}})
        workflows_list=await get_serialize_document(workflows)
        for workflow in workflows_list:
            try:
                if workflow["creater_id"] == credentials["id"]:
                    workflow["is_creator"]=True
                else:
                    workflow["is_creator"]=False
            except:
                 workflow["creater_id"] =""
                 if workflow["creater_id"] == credentials["id"]:
                    workflow["is_creator"]=True
                 else:
                    workflow["is_creator"]=False

        return workflows_list
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@workflow_router.delete("/{id}")
async def del_workflow(id: str, token: str = Depends(oauth2_scheme)):
    try:
        credentials = decode_token(token)
        await repository.delete_one("workflows", {"_id": ObjectId(id)})
        await repository.delete_many("workflow_items", {"workflow_id": id})
        return {"message": "Workflow and item deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
