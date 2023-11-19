from fastapi import APIRouter, Depends,HTTPException, status
from fastapi.responses import JSONResponse
from utils.jwt import decode_token
from data.repository import Repository
from middleware.middleware import oauth2_scheme
from utils.serialize import get_serialize_document,serialize_document_to_user
from models.enums import Statuses

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

@item_router.get("/{workflow_id}/")
async def get_workflow_items(workflow_id: str, token: str = Depends(oauth2_scheme)):
    credentials = decode_token(token)
    _id =credentials["id"]
    
    user_raw = await repository.find_by_id(id=_id,collection_name="users")

    if not user_raw:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    
    user = serialize_document_to_user(user_raw)
    if not user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Can't serialize user")

    rules = [rule.fields for rule in user.role.rule if rule.workflow_id == workflow_id and rule.status == Statuses.Hiding and not rule.is_delete]
    only_visible_rules = [rule.fields for rule in user.role.rule if rule.workflow_id == workflow_id and rule.status == Statuses.Visible and not rule.is_delete]

    projection = {"_id": 0, "workflow_id": 0}

    workflow_items = await repository.find_many("workflow_items", {"workflow_id": workflow_id}, projection=projection)

    if not rules and not only_visible_rules:
        
        response_data = {
            "Items": await get_serialize_document(workflow_items),
            "Count": len(workflow_items)
        }
        return JSONResponse(content=response_data)
    

    if only_visible_rules:
        for item in workflow_items:
            for rule in only_visible_rules:
                for key, value in rule.items():
                    try:
                        if key in item and item[key] != value:
                            item.pop(key, None)

                        keys_to_remove = [item_key for item_key in item.keys() if item_key != key]
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

    response_data={
        "Items": await get_serialize_document(workflow_items),
        "Count": len(workflow_items)
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

@item_router.put("/{workflow_id}/{item_id}")
async def update_workflow_item(workflow_id: str, item_id: str, updated_item: dict, token: str = Depends(oauth2_scheme)):
    credentials = decode_token(token)
    await repository.update_one("workflow_items", {"_id": item_id, "workflow_id": workflow_id}, updated_item)
    log = {
        "workflow_id": workflow_id,
        "user_id": credentials["id"],
        "op": "UPDATE",
        "change": item_id
    }
    await repository.insert_one("workflow_log", log)
    return {"message": "Workflow item updated successfully"}