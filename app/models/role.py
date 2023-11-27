from pydantic import BaseModel
from models.rule import Rules
from typing import List

class Role(BaseModel):
    name:str
    rule:List[Rules]
    user_id:str
    is_delete:bool
    workflow_id:str
    can_modify:bool
  

   
    





