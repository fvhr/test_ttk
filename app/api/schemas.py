from pydantic import BaseModel


# Модель для тела запроса
class MessageModel(BaseModel):
    message: str
