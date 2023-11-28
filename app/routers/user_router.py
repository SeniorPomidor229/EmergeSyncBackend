from fastapi import APIRouter, HTTPException, Depends,status
from data.repository import Repository
from models.user import *
from utils.jwt import encode_token, decode_token
from utils.serialize import get_serialize_document
from middleware.middleware import oauth2_scheme
import bcrypt
router = APIRouter()

repository = Repository(
    "mongodb://admin:T3sT_s3rV@nik.ydns.eu:400/",
    "EmergeSync"
)
 
@router.post("/",response_model=None,
                    summary="Create a user role"
                    ,response_description="upon successful creation, return id proffile")
async def create(request: UserDTO):
    user = await repository.find_one("users", {"username":request.username})
    if user != None:
        raise HTTPException(404, "user already excist")
    new_user={
        "username":request.username,
        "password":hash_password(request.password)
    }
    result = await repository.insert_one("users", new_user)
    profile = {
        "user_id": str(result),
       "first_name": request.username if not request.first_name else request.first_name,

        "last_name":request.last_name,
        "phone":"",
        "email":""
        }
    await repository.insert_one("profiles", profile)
    return str(result)



@router.post("/login",response_model=None,
                    summary="Login from user data"
                    ,response_description="upon successful login, return token")
async def token(request: UserDTO):
    user = await repository.find_one("users", {"username":request.username})
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "user not found")
    
    if not check_password(request.password,user["password"]):
         raise HTTPException(status.HTTP_400_BAD_REQUEST, "wrong password")
    payload = {
        "id": str(user["_id"])
    }
    token = encode_token(payload)
    return {"accsess_token": token}

@router.get("/",response_model=Profile,
                    summary="Get my proffile"
                    ,response_description="return mine proffile")
async def me(token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    print(creditals)
    profile = await repository.find_one("profiles", {"user_id":creditals["id"]})
    return await get_serialize_document(profile)

@router.get("/{user_id}",response_model=None,
                    summary="Get proffile by {user_id}"
                    ,response_description="return proffile by {user_id}")
async def get_user_profile(user_id:str,token: str = Depends(oauth2_scheme)):
    creditals = decode_token(token)
    print(creditals)
    profile = await repository.find_one("profiles", {"user_id":user_id})
    if not profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile dont find")

    return await get_serialize_document(profile)

@router.get("/users/{workflow_id}/",response_model=None,
                    summary="Get all proffiles"
                    ,response_description="Get all proffiles which don't haven't role"+
                     " in workflow with  {workflow_id}")
async def get_users(workflow_id:str,token: str = Depends(oauth2_scheme)):
 
    creditals = decode_token(token)
  
    print(creditals)
#     profile = await repository.find_agregate(
#     collection_name="profiles",
#     lookup=
#     {
#         "$lookup": {
#             "from": "roles",
#             "localField": "user_id",
#             "foreignField": "user_id",
#             "as": "userRoles"
#         }
#     },

#     match={
#         "$match": 
#         {
             
#            "$and": [
#             {
#                 # "$or": [
#                 #  #   {"userRoles": {"$size": 0}},
                   
#                 #    {"userRoles.workflow_id":{"$ne": workflow_id} },
#                 #     # {"userRoles.is_delete": {"$exists": False}},
#                 # ]
#                 "$and":[
#                     {"userRoles.user_id":{"$ne": workflow_id} },
#                  #  {"userRoles.is_delete": {"$exists": False}},
#                 ]
#             },
#             {"user_id": {"$ne": creditals["id"]}}
#         ]
#         }
#     }

# )

    workflow=await repository.find_by_id("workflows",workflow_id)
    if not workflow:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Workflow dont find")
    profile = await repository.find_many("profiles", query={"$and": [
    {"user_id": {"$nin": workflow["user_id"]}},
    {"user_id": {"$ne": creditals["id"]}}
    ]})

    #profile = await repository.find_many("profiles", )
    if not profile:
        profile=[]
    
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



def hash_password(password) ->str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def check_password(input_password, hashed_password):
    return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password)


    