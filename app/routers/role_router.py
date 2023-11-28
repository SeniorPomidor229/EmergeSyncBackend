from fastapi import APIRouter, HTTPException, Depends,status,Body
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
rule_router=APIRouter()
repository = Repository(
    "mongodb://admin:T3sT_s3rV@nik.ydns.eu:400/",
    "EmergeSync"
)

@role_router.post("/",
                  response_model=None,
                    summary="Create a user role"
                    ,response_description="upon successful creation, return status 201 with no content")
async def create_role(request: Role=Body(), token: str = Depends(oauth2_scheme)):

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
    ls=await get_serialize_document(workflow["user_id"])
    
    ls.append(request.user_id)
    
    workflow["user_id"]=ls
    result = await repository.update_one("workflows",{ "_id":ObjectId(request.workflow_id)}, workflow)
   
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
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not created")


@role_router.get("/my_role/{workflow_id}" , response_model=Role,
                    summary="Get My Role by file with id {workflow_id}"
                    ,response_description="return authorizited user role by file with id  {workflow_id} ")
async def get_my_role( workflow_id:str,token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    _id=creditals["id"]
    if(not _id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    role=   await repository.find_one("roles",{"user_id":_id , "workflow_id":  workflow_id ,"is_delete":False})
    
    if(not role):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found")
    return JSONResponse(content=await get_serialize_document(role)) 


@role_router.get("/{workflow_id}/{user_id}/", response_model=Role,
                    summary="Get User Role by id user  {user_id} and by file with id {workflow_id}"
                    ,response_description="return from user with {user_id}  role  and filter by {workflow_id} ")

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


@role_router.put("/", response_model=bool,
                    summary="Update User Role"
                    ,response_description="update role from request")
async def change_role(request: Role, token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    _id= creditals["id"]
    if(not _id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User Not Found")
    
    update_doc=repository.find_one("roles",{"user_id":request.user_id,"workflow_id":request.workflow_id,"is_delete":False})
    if(not update_doc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Role Not Found")
    for rule in request.rule:
        if not rule.id:
            rule.id=str(ObjectId)
    result = await repository.update_one("roles", {"user_id":request.user_id,"workflow_id":request.workflow_id, "is_delete":False}, request.model_dump())
    return result>0

@role_router.delete("/",response_model=bool,
                    summary="Delete User Role"
                    ,response_description="Delete role by role_id")
async def del_role(role_id: str,token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    _id= creditals["id"]
    if(not _id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User Not Found")
   
    role_raw=await get_serialize_document(await repository.find_one("roles",{"_id":ObjectId(role_id)}))
    if(not role_raw):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found")
   
    
    workflow={}
    try:
        workflow=await  repository.find_one("workflows",{ "_id":ObjectId(role_raw["workflow_id"])})
    except:
        result = await repository.delete_by_id("roles",ObjectId(role_id))
        return result>0
    
    ls=await get_serialize_document(workflow["user_id"])
    if(role_raw["user_id"] in ls):
        ls.remove(role_raw["user_id"])
    workflow["user_id"]=ls
    await repository.update_one("workflows",{ "_id":ObjectId(workflow["_id"])}, workflow)
    result = await repository.delete_by_id("roles",ObjectId(role_id))
    return result>0


@role_router.get("/{workflow_id}/",response_model=list[Role],
                    summary="Get all roles by file with id {workflow_id}"
                    ,response_description="Get All Roles by file with id {workflow_id}")
async def get_roles(workflow_id:str,token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    _id=creditals["id"]


    if(not _id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    roles= await get_serialize_document(await repository.find_many("roles",
                                    {
                                           
                                             "creater_id":_id,
                                             "workflow_id":workflow_id, 
                        
                                    }))
    if(not roles):
            roles= await get_serialize_document(await repository.find_many("roles",
                                    {
                                
                                             "workflow_id":workflow_id, 
                        
                                    }))
    return roles
    user_ids_from_roles = [role["user_id"] for role in roles]
    user_ids_from_roles.append("655f4b611393e4e6aa0ee7d1")
    user_ids_from_roles.append("655f4b611393e4e6aa0ee7d1")
    #return user_ids_from_roles
    profiles =await get_serialize_document( await repository.find_many("profiles", {"user_id": {"$in": user_ids_from_roles}}) )
    
# return await get_serialize_document( profiles)
   
    combined= zip(profiles, roles)
    sorted_list = sorted(combined, key=lambda x: x[1])
    result_list=list()
  
    for item in sorted_list:
        item[1]["profile"]=item[0]
        result_list.append(item[1])

    return JSONResponse(content= await get_serialize_document(result_list)) 





@rule_router.post("/rules/",tags=["Rules"],response_model=Rules,
                    summary="Create Rule"
                    ,response_description="Create Rule by workflow_id and user_id\nsuccefuly response is http status 204 no content")
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

@rule_router.delete("/rules/",tags=["Rules"],response_model=bool,
                    summary="Delete From User Role Rule"
                    ,response_description="Delete Rule by role_id and user_id")
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
    return result>0




    