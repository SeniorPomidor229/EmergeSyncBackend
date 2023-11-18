from pydantic import BaseModel
from models.role import Role

class UserDTO(BaseModel):
    username: str
    password: str
    кole: Role

class Profile(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str



    



