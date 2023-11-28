from fastapi import APIRouter, HTTPException, Depends, UploadFile, File   
from data.repository import Repository
from middleware.middleware import oauth2_scheme
from utils.serialize import get_serialize_document
from utils.jwt import decode_token
log_router = APIRouter()

repository = Repository(
    "mongodb://admin:T3sT_s3rV@nik.ydns.eu:400/", 
    "EmergeSync")

@log_router.get("/",response_model=list[dict[str,str]],
                    summary="Get all logs"
                    ,response_description="get all logs")
async def get_log( token: str = Depends(oauth2_scheme)):
    credentials = decode_token(token)
    result = await repository.find_agregate(
    collection_name="workflow_log",
    lookup=
    {
       "$lookup": {
            "from": "workflows",
            "let": {"workflowId": "$workflow_id"},
            "pipeline": [
                {"$match": {"$expr": {"$eq": ["$$workflowId", {"$toString": "$_id"}]}}}
            ],
            "as": "workflows"
        }
    },

    match={
        "$match": 
        {
                "$and":[
                    {"workflows.creater_id": credentials["id"] },
                ]
           
        }
    }
)
    return  await get_serialize_document(result)