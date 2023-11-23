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
from models.rule import Rules
role_router = APIRouter()

repository = Repository(
    "mongodb://admin:T3sT_s3rV@nik.ydns.eu:400/",
    "EmergeSync"
)
 
@role_router.post("/")
async def create_role(request: Role, token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    _id=creditals["id"]

    workflow={}
    try:
        workflow=await  repository.find_one("workflows",{ "_id":ObjectId(request.workflow_id)})
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Workflow underfind or not access")

    if(not workflow):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Workflow underfind or not access")
  
    role_raw=  await repository.find_one("roles",{"user_id":request.user_id, "workflow_id":request.workflow_id, "is_delete":False})
    
    if(role_raw):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role Exist")
    
    role= serialize_document_to_role(role_raw)
    
    if(role):
       raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role Exist")

    for rule in request.rule:
         rule.id= str(ObjectId())
    insertItem={
        "name":request.name,
        "rule": await get_serialize_document(request.rule),
        "user_id":request.user_id,
        "is_delete":request.is_delete,
        "workflow_id":request.workflow_id,
        "creater_id":_id
    }
    result = await repository.insert_one("roles", insertItem)
    if(result):
        return JSONResponse(status_code=status.HTTP_201_CREATED,content= None) 
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role dont create")


@role_router.get("/")
async def get_my_role(token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    _id=creditals["id"]
    if(not _id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    role=   await repository.find_one("roles",{"user_id":_id ,    "is_delete":False})
    
    if(not role):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found")
    return JSONResponse(content=await get_serialize_document(role)) 


@role_router.get("/{workflow_id}/{user_id}/")
async def get_role(workflow_id:str,user_id:str,token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    _id=creditals["id"]
    if(not _id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    role= await repository.find_one("roles",
                                    {
                                             "user_id":user_id ,
                                             "creater_id":_id,
                                             "workflow_id":workflow_id, 
                                             "is_delete":False
                                    })
    prof=await repository.find_one("profiles", {"user_id":user_id})
    if(not role or not prof):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found Or Profile")
    response=await get_serialize_document(role)
    
    response["profile"]=await get_serialize_document(prof)

    return JSONResponse(content=response) 


@role_router.put("/")
async def change_role(request: Role, token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    _id= creditals["id"]
    if(not _id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User Not Found")
    
    update_doc=repository.find_one("roles",{"user_id":request.user_id,"workflow_id":request.workflow_id,"is_delete":False})
    if(not update_doc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Role Not Found")

    result = await repository.update_one("roles", {"user_id":request.user_id,"workflow_id":request.workflow_id, "is_delete":False}, request)
    return await get_serialize_document(result)

@role_router.delete("/")
async def del_role(role_id: str,token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    _id= creditals["id"]
    if(not _id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User Not Found")
  
    role_raw=await repository.find_one("roles",{"_id":ObjectId(role_id),"is_delete":False})
    if(not role_raw):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found")
    role= await serialize_document_to_role(role_raw)
    
    if(not role):
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail="Can't serilize role")
    role.is_delete=True
    result = await repository.delete_by_id("roles",{"_id":ObjectId(role_id),"is_delete":False})
    return await get_serialize_document(result)


@role_router.get("/{workflow_id}/")
async def get_roles(workflow_id:str,token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    _id=creditals["id"]
    if(not _id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    roles= await get_serialize_document(await repository.find_many("roles",
                                    {
                                           
                                             "creater_id":_id,
                                             "workflow_id":workflow_id, 
                                             "is_delete":False
                                    }))
    user_ids_from_roles = [role["user_id"] for role in roles]
    profiles =await get_serialize_document( await repository.find_many("profiles", {"user_id": {"$in": user_ids_from_roles}}) )
    combined= zip(profiles, roles)
    sorted_list = sorted(combined, key=lambda x: x[1])
    result_list=list()
    for item in sorted_list:
        item[1]["profile"]=item[0]
        result_list.append(item[1])

    return JSONResponse(content= await get_serialize_document(result_list)) 





@role_router.post("/rules/")
async def create_rule(request: Rules,workflow_id:str, user_id:str,token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    _id=creditals["id"]
    if(not _id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    role_raw= await get_serialize_document( await repository.find_one("roles",{"user_id":user_id, "workflow_id":workflow_id,"is_delete":False}))
    if(not role_raw):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found")
    role=  serialize_document_to_role(role_raw)
    
    if(not role):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Can't serilize role")
    request.id= str(ObjectId())

    role.rule.append(request)
    result = await repository.update_one("roles", {"user_id":user_id, "workflow_id":workflow_id,"is_delete":False}, role.model_dump())
    if(result):
        return HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=None)

    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can't Modify")

@role_router.delete("/rules/")
async def del_rule( request: Rules, user_id:str,workflow_id:str,token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    _id= creditals["id"]
    if(not _id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User Not Found")
    role_raw=await get_serialize_document(repository.find_one("roles",{"user_id":user_id, "workflow_id":workflow_id,"is_delete":False}))
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
    result = await repository.update_one("roles", {"user_id":user_id, "workflow_id":workflow_id,"is_delete":False}, update=update_doc.model_dump())
    return await get_serialize_document(result)




    