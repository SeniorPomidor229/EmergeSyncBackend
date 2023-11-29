from fastapi import APIRouter, Depends,HTTPException, status,Request
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


@item_router.post("/{workflow_id}/",
                    summary="Create field include in file by id  {workflow_id}"
                    ,response_description="Create field include in file"+
                     " with id {workflow_id}")
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
    response_data={"workflow_id":workflow_id}
    return JSONResponse(content=response_data)
   

@item_router.get("/{workflow_id}/" ,  
                    summary="Get fields in file by id {workflow_id}"
                    ,response_description="Get fields in file by  id {workflow_id} and filter by role")
async def get_workflow_items(workflow_id: str,  request:Request, token: str = Depends(oauth2_scheme)):
    skip = int(request.query_params.get("$skip", 0))
    top = int(request.query_params.get("$top", 0))

    if(not top):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Top must be positive")
    
    credentials = decode_token(token)
    _id =credentials["id"]
    offset_min = skip
    offset_max = top+skip
    workflow_items = await repository.find_many("workflow_items", {"workflow_id": workflow_id}, projection={"test":0})

    #projection = { "workflow_id": 0}

    
    role_raw= await repository.find_one("roles",{"user_id":_id, "workflow_id":workflow_id,"is_delete":False})
    role = serialize_document_to_role(role_raw)
 
    if not role:
        workflow_items=[item for item in workflow_items if item] 
        items=(await get_serialize_document(workflow_items[offset_min:offset_max]))
   
        response_data = {
            "skipCount": skip,
            "maxResultCount": top,
            "Items":items ,
            "Count": len(workflow_items)
        }
        return JSONResponse(content=response_data)
    
    rules = [rule.fields for rule in role.rule if  rule.status == Statuses.Hiding.value and not rule.is_delete]
    only_visible_rules = [rule.fields for rule in role.rule if  rule.status == Statuses.Visible.value and not rule.is_delete]
    only_all_Hiding_rules = [rule.fields for rule in role.rule if  rule.status == Statuses.AllHiding.value and not rule.is_delete]
    only_all_Visible_rules = [rule.fields for rule in role.rule if  rule.status == Statuses.AllVisible.value and not rule.is_delete]

    if  not rules and not only_visible_rules and not only_all_Hiding_rules and not only_all_Visible_rules:
        workflow_items=[item for item in workflow_items if item] 
        items=(await get_serialize_document(workflow_items))
     
        response_data = {
     
            "Items":items ,
            "Count": len(items)
        }
        return JSONResponse(content=response_data)
    
    
    
    if only_all_Visible_rules :
      
        keys=[]
        for rule in only_all_Visible_rules:
            for key in rule.keys():
                keys.append(key)
        
        for item in workflow_items:
            keys_to_remove = [item_key for item_key in item.keys() if item_key  not in keys and item_key!="_id" and item_key!="workflow_id"]
            for key_del in keys_to_remove:
                item.pop(key_del, None)
                            
        
                        
                    
    if only_visible_rules :
        
        keys=[]
        values=[]
        for rule in only_visible_rules:
            for key,value in rule.items():
                keys.append(key)
                values.append(value)
        
        for item in workflow_items:
            keys_to_remove=[]
            for item_key,item_value in item.items():
                if item_key not in keys or (item_key in keys and item_value != values[keys.index(item_key)] and item_key!="_id"and item_key!="workflow_id"):
                    keys_to_remove.append(item_key)
                
            for key_del in keys_to_remove:
                item.pop(key_del, None)
    
    if only_all_Hiding_rules:
        for rule in only_all_Hiding_rules:
                for key, value in rule.items():
                    try:
                        for item in workflow_items:
                            if key in item:
                                if (key!="_id"and key!="workflow_id"):
                                     item.pop(key, None)
                    except Exception as ex:
                        continue
    
    if  rules:
        for item in workflow_items:
            for rule in rules:
                for key, value in rule.items():
                    try:
                        if key in item and item[key] == value and key!="_id"and key!="workflow_id":
                            item.pop(key, None)
                    except:                  
                        continue


    workflow_items=[item for item in workflow_items if item]                     
    items=(await get_serialize_document(workflow_items))[offset_min:offset_max]
  
            
    response_data = {
            "skipCount": skip,
            "maxResultCount": top,
            "Items":items ,
            "Count": len(workflow_items)
        }                
 
    return JSONResponse(content=response_data)


@item_router.get("/without_pagination/{workflow_id}",deprecated=True )
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
    only_all_Hiding_rules = [rule.fields for rule in role.rule if  rule.status == Statuses.AllHiding.value and not rule.is_delete]
    only_all_Visible_rules = [rule.fields for rule in role.rule if  rule.status == Statuses.AllVisible.value and not rule.is_delete]
    
    if  not rules and not only_visible_rules and not only_all_Hiding_rules and not only_all_Visible_rules:
        items=(await get_serialize_document(workflow_items))
        response_data = {
     
            "Items":items ,
            "Count": len(items)
        }
        return JSONResponse(content=response_data)
    


    if only_all_Visible_rules :
       
        for rule in only_all_Visible_rules:
            for key, value in rule.items():
                    try:
                        for item in workflow_items:
                            keys_to_remove = [item_key for item_key in item.keys() if item_key  not in rule]
                            
                            for key_del in keys_to_remove:
                                item.pop(key_del, None)
                    except Exception as ex:
                        continue
    
    
    if not only_all_Visible_rules and only_visible_rules :
        for item in workflow_items:
            for rule in only_visible_rules:
                for key, value in rule.items():
                    try:

                        keys_to_remove = [item_key for item_key in item.keys() if item_key  not in rule and rule[item_key]!=value]
                        
                        for key_del in keys_to_remove:
                            item.pop(key_del, None)
                    except Exception as ex:
                        continue

   
    if only_all_Hiding_rules:
        for rule in only_all_Hiding_rules:
                for key, value in rule.items():
                    try:
                        for item in workflow_items:
                            if key in item:
                                item.pop(key, None)
                    except Exception as ex:
                        continue
    
    if not only_all_Hiding_rules  and rules:
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



@item_router.get("/getKeys/{workflow_id}/",
                    summary="Get example first field from file by id {workflow_id}"
                    ,response_description="Get example first field, from file with  id {workflow_id}")
async def get_workflows(workflow_id: str, 
                 token: str = Depends(oauth2_scheme)):
    credentials = decode_token(token)
    _id =credentials["id"]
    
   
  
    workflow_items= await repository.find_one("workflow_items", {"workflow_id": workflow_id})
    
    item=(await get_serialize_document(workflow_items))
 
    return JSONResponse(content=item)



@item_router.delete("/{workflow_id}/{item_id}", 
                    summary="delete field from file with id {workflow_id}"
                    ,response_description="delete field by id {item_id} from file  with id {workflow_id}")
async def delete_workflow_item(workflow_id: str, item_id: str, token: str = Depends(oauth2_scheme)):

    credentials = decode_token(token)
    role=await get_serialize_document(await repository.find_one("roles", {
        "workflow_id":workflow_id,
        "user_id":credentials["id"],
        "is_delete":False
        }))
    
    if role:
      if "can_modify" in role and not role["can_modify"]:
           raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user can`t modify")
    
    
    delete =await repository.delete_one("workflow_items", {"_id": item_id, "workflow_id": workflow_id})
    log = {
        "workflow_id": workflow_id,
        "user_id": credentials["id"],
        "op": "DELETE",
        "change": item_id
    }
    await repository.insert_one("workflow_log", log)
    return delete>0




@item_router.put("/{workflow_id}/", 
                    summary="update field from file with id {workflow_id}"
                    ,response_description="update field {updated_item} from file with id {workflow_id}")
async def update_workflow_item(workflow_id: str, updated_item: dict, token: str = Depends(oauth2_scheme)):
    try:
        credentials = decode_token(token)
        # res=updated_item
        # updated_item["_id"]=None
        updated_item["_id"]=ObjectId(updated_item["_id"])
        # return await get_serialize_document(updated_item)
        role=await get_serialize_document(await repository.find_one("roles", {
            "workflow_id":workflow_id,
            "user_id":credentials["id"],
            "is_delete":False
            }))
        
        if role:
            if "can_modify" in role and not role["can_modify"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user can`t modify")
            
        
        updated_item =remove_empty_keys(updated_item)
        updated_item = {key: value for key, value in updated_item.items() if value not in ([], {}, "")}

        update= await repository.update_one("workflow_items", {"_id":updated_item["_id"]}, updated_item)
        log = {
            "workflow_id": workflow_id,
            "user_id": credentials["id"],
            "op": "UPDATE",
            "change": updated_item["_id"]
        }
        await repository.insert_one("workflow_log", log)
        return update>0
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))


def remove_empty_keys(item):
    if isinstance(item, dict):
        return {key: remove_empty_keys(value) for key, value in item.items() if value not in (None, "", {}, [])}
    elif isinstance(item, list):
        return [remove_empty_keys(element) for element in item]
    else:
        return item

