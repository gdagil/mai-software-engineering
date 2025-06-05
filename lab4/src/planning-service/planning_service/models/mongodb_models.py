from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId
from enum import Enum


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class TransactionMongo(BaseModel):
    """MongoDB модель для транзакции"""
    id: Optional[str] = Field(None, alias="_id")
    plan_id: int = Field(..., description="ID бюджетного плана")
    type: TransactionType = Field(..., description="Тип транзакции")
    amount: float = Field(..., description="Сумма транзакции", gt=0)
    description: Optional[str] = Field(None, description="Описание транзакции")
    category: Optional[str] = Field(None, description="Категория транзакции")
    user_id: str = Field(..., description="ID пользователя")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Дата создания")
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str
        }
    
    @classmethod
    def from_mongo(cls, data: dict):
        """Создает объект из MongoDB документа"""
        if not data:
            return None
        
        if "_id" in data:
            data["_id"] = str(data["_id"])
        
        return cls(**data)
    
    def to_mongo(self) -> dict:
        """Преобразует объект в MongoDB документ"""
        data = self.model_dump(by_alias=True, exclude_unset=True)
        
        # Удаляем id если он None (для новых документов)
        if data.get("_id") is None:
            data.pop("_id", None)
        elif data.get("_id"):
            # Преобразуем строку обратно в ObjectId если нужно
            try:
                data["_id"] = ObjectId(data["_id"])
            except:
                pass
        
        return data


class TransactionCreateMongo(BaseModel):
    """Модель для создания транзакции в MongoDB"""
    plan_id: int = Field(..., description="ID бюджетного плана")
    type: TransactionType = Field(..., description="Тип транзакции")
    amount: float = Field(..., description="Сумма транзакции", gt=0)
    description: Optional[str] = Field(None, description="Описание транзакции")
    category: Optional[str] = Field(None, description="Категория транзакции")
    user_id: str = Field(..., description="ID пользователя")


class TransactionUpdateMongo(BaseModel):
    """Модель для обновления транзакции в MongoDB"""
    type: Optional[TransactionType] = Field(None, description="Тип транзакции")
    amount: Optional[float] = Field(None, description="Сумма транзакции", gt=0)
    description: Optional[str] = Field(None, description="Описание транзакции")
    category: Optional[str] = Field(None, description="Категория транзакции")


class TransactionFilter(BaseModel):
    """Модель для фильтрации транзакций"""
    plan_id: Optional[int] = None
    type: Optional[TransactionType] = None
    category: Optional[str] = None
    min_amount: Optional[float] = Field(None, ge=0)
    max_amount: Optional[float] = Field(None, ge=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[str] = None 