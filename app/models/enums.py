from enum import Enum
class Statuses(Enum):
    Hiding=0        # исключить из списка поле по ключу и значению
    Visible=1       # Сделать видимым только определенное поле по ключу и значению
    Unknown=2
    AllHiding=3,# скрыть все по ключу
    AllVisible=4#сделать все видимым по ключу

class KeyWorkflowItem(Enum):
    OrganizationName="Название организации"
    ActionDate="Дата действия"
    OrganizationStatus="Статус"
    RegisterOrganizationNumber="Регистрационный номер"
    StartDate="Дата начала"