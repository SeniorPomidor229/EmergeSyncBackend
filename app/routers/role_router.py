from fastapi import APIRouter, HTTPException, Depends,status
from fastapi.responses import JSONResponse
from data.repository import Repository
from models.user import *
from models.rule import Rules
from utils.jwt import encode_token, decode_token
from utils.serialize import get_serialize_document, serialize_document_to_role
from middleware.middleware import oauth2_scheme
from bson import ObjectId
from models.role import Role
role_router = APIRouter()

repository = Repository(
    "mongodb://admin:T3sT_s3rV@nik.ydns.eu:400/",
    "EmergeSync"
)
 
@role_router.post("/")
async def create_role(request: Role,token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    _id=creditals["id"]
    role_raw=  await repository.find_one("roles",{"user_id":_id,"is_delete":False})
    
    if(role_raw):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role Exist")
    
    role= serialize_document_to_role(role_raw)
    
    if(role):
       raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role Exist")
    request.user_id=_id
    result = await repository.insert_one("roles", request.model_dump())
    if(result):
        return JSONResponse(status_code=status.HTTP_201_CREATED,content= None) 
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role dont create")


@role_router.get("/")
async def get_role(token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    _id=creditals["id"]
    if(not _id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    role=   await repository.find_one("roles",{"user_id":_id , "is_delete":False})
    
    if(not role):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found")
    return JSONResponse(content=await get_serialize_document(role)) 

@role_router.put("/")
async def change_role(request: Role, token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    _id= creditals["id"]
    if(not _id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User Not Found")
    update_doc=repository.find_one("roles",{"user_id":_id,"is_delete":False})
    if(not update_doc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Role Not Found")

    result = await repository.update_one("roles", {"user_id":_id, "is_delete":False}, request)
    return await get_serialize_document(result)

@role_router.delete("/")
async def del_role(token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    _id= creditals["id"]
    if(not _id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User Not Found")
    
    role_raw=await repository.find_one("roles",{"user_id":_id,"is_delete":False})
    if(not role_raw):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found")
    role= await serialize_document_to_role(role_raw)
    
    if(not role):
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail="Can't serilize role")
    role.is_delete=True
    result = await repository.update_one("roles", {"user_id":_id,"is_delete":False}, role)
    return await get_serialize_document(result)



@role_router.post("/rules/")
async def create_rule(request: Rules,token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    _id=creditals["id"]
    if(not _id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    role_raw= await get_serialize_document( await repository.find_one("roles",{"user_id":_id,"is_delete":False}))
    if(not role_raw):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found")
    role=  serialize_document_to_role(role_raw)
  
    if(not role):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Can't serilize role")
    role.rule.append(request)

  
    result = await repository.update_one("roles", {"user_id":_id,"is_delete":False}, role.model_dump())
    if(result):
        return HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=None)

    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can't Modify")

@role_router.delete("/rules/")
async def del_rule( request: Rules,token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    _id= creditals["id"]
    if(not _id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User Not Found")
    role_raw=await get_serialize_document(repository.find_one("roles",{"user_id":_id,"is_delete":False}))
    if(not role_raw):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found")
    role= serialize_document_to_role(role_raw)
    if(not role):
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail="Can't serilize role")

    update_doc=None
    for rule in role.rule:
        if(rule.id ==request.id):
            update_doc=rule
            update_doc.is_delete=True
        
    if not update_doc :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found")
    result = await repository.update_one("roles", {"user_id":_id,"is_delete":False}, update=update_doc.model_dump())
    return await get_serialize_document(result)




    