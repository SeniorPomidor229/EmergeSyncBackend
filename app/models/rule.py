from pydantic import BaseModel
from models.enums import Statuses

class Rules(BaseModel):
    workflow_items_name:list[str] 
    workflow_id:str
    status:Statuses