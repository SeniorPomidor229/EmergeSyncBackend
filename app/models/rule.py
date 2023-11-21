from pydantic import BaseModel
from models.enums import Statuses,KeyWorkflowItem
from typing import Dict


# KeyWorkflowItem 
# лучше все серилизовать и приветси базу к определенным полям 
# и не ставить все надежды на фронт
class Rules(BaseModel):
    id:str
  
    status:int
    fields: Dict[str, str] 
    is_delete:bool




