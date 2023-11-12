from pydantic import BaseModel

class UserDTO(BaseModel):
    username: str
    password: str

class Profile(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str