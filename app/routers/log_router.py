from fastapi import APIRouter, HTTPException, Depends, UploadFile, File   
from data.repository import Repository
from middleware.middleware import oauth2_scheme
from utils.serialize import get_serialize_document

log_router = APIRouter()

repository = Repository(
    "mongodb://admin:T3sT_s3rV@nik.ydns.eu:400/", 
    "EmergeSync")

@log_router.get("/{workflow_id}")
async def get_log(workflow_id: str, token: str = Depends(oauth2_scheme)):
    result = await repository.find_many("workflow_log", {"workflow_id": workflow_id})
    return get_serialize_document(result)