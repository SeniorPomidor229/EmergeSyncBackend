from fastapi import APIRouter, HTTPException, Depends
from data.repository import Repository
from models.user import *
from utils.jwt import encode_token, decode_token
from utils.serialize import get_serialize_document
from middleware.middleware import oauth2_scheme

router = APIRouter()

repository = Repository(
    "mongodb://admin:T3sT_s3rV@nik.ydns.eu:400/",
    "EmergeSync"
)
 
@router.post("/")
async def create(request: UserDTO):
    user = await repository.find_one("users", {"username":request.username})
    if user != None:
        raise HTTPException(404, "user already excist")
    result = await repository.insert_one("users", request.model_dump())
    profile = {
        "user_id": str(result),
        "first_name":"",
        "last_name":"",
        "phone":"",
        "email":""
        }
    await repository.insert_one("profiles", profile)
    return str(result)

@router.post("/login")
async def token(request: UserDTO):
    user = await repository.find_one("users", {"username":request.username})
    if not user:
        raise HTTPException(404, "user not found")
    payload = {
        "id": str(user["_id"])
    }
    token = encode_token(payload)
    return {"accsess_token": token}

@router.get("/")
async def me(token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    print(creditals)
    profile = await repository.find_one("profiles", {"user_id":creditals["id"]})
    return await get_serialize_document(profile)
@router.get("/{user_id}")
async def me(user_id:str,token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    print(creditals)
    profile = await repository.find_one("profiles", {"user_id":user_id})
    return await get_serialize_document(profile)

@router.get("/users")
async def get_users(token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    print(creditals)
    profile = await repository.find_many("profiles", {"reportedBy": { '$ne': {"user_id":creditals["id"]} }})
    return await get_serialize_document(profile)


@router.put("/")
async def change(request: Profile, token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    change_document = {
        "first_name": request.first_name,
        "last_name": request.last_name,
        "phone": request.phone,
        "email": request.email
    }
    result = await repository.update_one("profiles", {"user_id":creditals["id"]}, change_document)
    return await get_serialize_document(result)



    