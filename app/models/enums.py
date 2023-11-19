from enum import Enum
class Statuses(Enum):
    Hiding=0
    Visible=1
    Unknown=2

class KeyWorkflowItem(Enum):
    OrganizationName="Название организации"
    ActionDate="Дата действия"
    OrganizationStatus="Статус"
    RegisterOrganizationNumber="Регистрационный номер"
    StartDate="Дата начала"