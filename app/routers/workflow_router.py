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


@workflow_router.post("/",
                    summary="Create file"
                    ,response_description="Create file")
async def create_workflow(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    workflow_id=""
    try:
        credentials = decode_token(token)
        print(file.file)

        df = pd.read_excel(file.file)
        df = df.applymap(lambda x: str(x) if pd.notna(x) else '')
        users=[]
        _id=credentials["id"]
        users.append(_id)
        workflow_data = {
            "name": f"{file.filename}",  # название файла
            "create_at": datetime.utcnow(),
            "last_modify": datetime.utcnow(),
            "creater_id":_id,
            "user_id": users
        }
       
        workflow_items_list = [{str(key): value for key, value in item.items()}
                               for item in df.to_dict(orient="records")]
        workflow_id = await repository.insert_one("workflows", workflow_data)

        for item in workflow_items_list:
            item["workflow_id"] = str(workflow_id)

        await repository.insert_many("workflow_items", workflow_items_list)
        response_data = await get_serialize_document({"workflow_id": str(workflow_id)})
        return JSONResponse(content=response_data)
        # return {"message": "Workflow and workflow items created successfully"}
    except Exception as e:
        try:
            await repository.delete_by_id("workflows", workflow_id)
        finally:
            raise HTTPException(status_code=422, detail=str(e))


@workflow_router.get("/",
                    summary="Get all mine files"
                    ,response_description="get all mine files")
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


@workflow_router.delete("/{id}", 
                    summary="delete file by {id}"
                    ,response_description="delete file  by {id}")
async def del_workflow(id: str, token: str = Depends(oauth2_scheme)):
    try:
        credentials = decode_token(token)
        delete= await repository.delete_one("workflows", {"_id": ObjectId(id)})
        await repository.delete_many("workflow_items", {"workflow_id": id})
        return delete>0
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
