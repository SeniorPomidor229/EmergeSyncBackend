from pydantic import BaseModel
from models.rule import Rules

class Role(BaseModel):
    name:str
    rule:list[Rules]
    user_id:str





