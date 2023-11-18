from pydantic import BaseModel
from models.enums import Statuses

class Rules(BaseModel):
    name_object:list[str]
    workflow_id:str
    status:Statuses