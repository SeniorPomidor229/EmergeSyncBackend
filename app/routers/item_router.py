from fastapi import APIRouter, Depends,HTTPException, status
from fastapi.responses import JSONResponse
from utils.jwt import decode_token
from data.repository import Repository
from middleware.middleware import oauth2_scheme
from utils.serialize import get_serialize_document,serialize_document_to_role
from models.enums import Statuses
from fastapi import Query
from bson import ObjectId
item_router = APIRouter()
repository = Repository("mongodb://admin:T3sT_s3rV@nik.ydns.eu:400/", "EmergeSync")


@item_router.post("/{workflow_id}/")
async def create_workflow_item(workflow_id: str, item: dict, token: str = Depends(oauth2_scheme)):
    credentials = decode_token(token)

    item["workflow_id"] = workflow_id
    result = await repository.insert_one("workflow_items", item)
    log = {
        "workflow_id": workflow_id,
        "user_id": credentials["id"],
        "op": "CREATE",
        "change": result
    }
    await repository.insert_one("workflow_log", log)
    return {"message": "Workflow item created successfully"}

@item_router.get("/{workflow_id}" )
async def get_workflow_items(workflow_id: str,  skipCount: int = Query(ge=0, default=0),
                maxResultCount : int = Query(ge=1, le=100), token: str = Depends(oauth2_scheme)):
    credentials = decode_token(token)
    _id =credentials["id"]
    offset_min = skipCount * maxResultCount
    offset_max = (skipCount + 1) * maxResultCount
    #projection = { "workflow_id": 0}

    
    role_raw= await repository.find_one("roles",{"user_id":_id, "workflow_id":workflow_id,"is_delete":False})
    role = serialize_document_to_role(role_raw)
 
    if not role:
        workflow_items = await repository.find_many_filter( 
        collection_name="workflow_items",                                                 
        query={"workflow_id": workflow_id},
        skip=offset_min,
        limit=maxResultCount
       )
        items=(await get_serialize_document(workflow_items))
        response_data = {
            "skipCount": skipCount,
            "maxResultCount": maxResultCount,
            "Items":items ,
            "Count": len(items)
        }
        return JSONResponse(content=response_data)
    
    rules = [rule.fields for rule in role.rule if  rule.status == Statuses.Hiding.value and not rule.is_delete]
    only_visible_rules = [rule.fields for rule in role.rule if  rule.status == Statuses.Visible.value and not rule.is_delete]

    if  not rules and not only_visible_rules:
        workflow_items = await repository.find_many_filter( 
        collection_name="workflow_items",                                                 
        query={"workflow_id": workflow_id},
        skip=offset_min,
        limit=maxResultCount
       )
        items=(await get_serialize_document(workflow_items))
        response_data = {
             "skipCount": skipCount,
            "maxResultCount": maxResultCount,
            "Items":items ,
            "Count": len(items)
        }
        return JSONResponse(content=response_data)
    
    
    workflow_items = await repository.find_many("workflow_items", {"workflow_id": workflow_id}, projection={"test":0})

    if only_visible_rules:
        for item in workflow_items:
            for rule in only_visible_rules:
                for key, value in rule.items():
                    try:
                        if key in item and item[key] != value:
                            item.pop(key, None)

                        keys_to_remove = [item_key for item_key in item.keys() if item_key  not in rule]
                        
                        for key_del in keys_to_remove:
                            item.pop(key_del, None)
                    except Exception as ex:
                        continue

      

    for item in workflow_items:

        
        for rule in rules:
            for key, value in rule.items():
                try:
                    if key in item and item[key] == value:
                        item.pop(key, None)
                except:
                   
                    continue
    items=(await get_serialize_document(workflow_items))[offset_min:offset_max]
    response_data = {
            "skipCount": skipCount,
            "maxResultCount": maxResultCount,
            "Items":items[offset_min:offset_max] ,
            "Count": len(items)
        }                
 
    return JSONResponse(content=response_data)




@item_router.get("/without_pagination/{workflow_id}/" )
async def get_workflows(workflow_id: str, 
                 token: str = Depends(oauth2_scheme)):
    credentials = decode_token(token)
    _id =credentials["id"]
   
    role_raw= await repository.find_one("roles",{"user_id":_id, "workflow_id":workflow_id,"is_delete":False})
    role = serialize_document_to_role(role_raw)
    workflow_items= await repository.find_many("workflow_items", {"workflow_id": workflow_id}, projection={"test":0})
    if not role:
      
        items=(await get_serialize_document(workflow_items))
        response_data = {
            
            "Items":items ,
            "Count": len(items)
        }
        return JSONResponse(content=response_data)
    
    rules = [rule.fields for rule in role.rule if  rule.status == Statuses.Hiding.value and not rule.is_delete]
    only_visible_rules = [rule.fields for rule in role.rule if  rule.status == Statuses.Visible.value and not rule.is_delete]

    if  not rules and not only_visible_rules:
        items=(await get_serialize_document(workflow_items))
        response_data = {
     
            "Items":items ,
            "Count": len(items)
        }
        return JSONResponse(content=response_data)
    
    

    if only_visible_rules:
        for item in workflow_items:
            for rule in only_visible_rules:
                for key, value in rule.items():
                    try:
                        if key in item and item[key] != value:
                            item.pop(key, None)

                        keys_to_remove = [item_key for item_key in item.keys() if item_key  not in rule]
                        
                        for key_del in keys_to_remove:
                            item.pop(key_del, None)
                    except Exception as ex:
                        continue

      

    for item in workflow_items:

        
        for rule in rules:
            for key, value in rule.items():
                try:
                    if key in item and item[key] == value:
                        item.pop(key, None)
                except:
                   
                    continue
    items=(await get_serialize_document(workflow_items))
    response_data = {
         
            "Items":items ,
            "Count": len(items)
        }                
 
    return JSONResponse(content=response_data)




@item_router.delete("/{workflow_id}/{item_id}")
async def delete_workflow_item(workflow_id: str, item_id: str, token: str = Depends(oauth2_scheme)):
    credentials = decode_token(token)
    await repository.delete_one("workflow_items", {"_id": item_id, "workflow_id": workflow_id})
    log = {
        "workflow_id": workflow_id,
        "user_id": credentials["id"],
        "op": "DELETE",
        "change": item_id
    }
    await repository.insert_one("workflow_log", log)
    return {"message": "Workflow and item delete successfully"}




@item_router.put("/{workflow_id}/")
async def update_workflow_item(workflow_id: str, updated_item: dict, token: str = Depends(oauth2_scheme)):
    credentials = decode_token(token)
    updated_item["_id"]=ObjectId(updated_item["_id"])
    await repository.update_one("workflow_items", {"_id": updated_item["_id"]}, updated_item)
    log = {
        "workflow_id": workflow_id,
        "user_id": credentials["id"],
        "op": "UPDATE",
        "change": updated_item["_id"]
    }
    await repository.insert_one("workflow_log", log)
    return {"message": "Workflow item updated successfully"}