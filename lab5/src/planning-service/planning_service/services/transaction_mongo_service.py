from typing import List, Optional
from bson import ObjectId
from pymongo.errors import PyMongoError
from datetime import datetime
import logging

from planning_service.models.mongodb_models import (
    TransactionMongo,
    TransactionCreateMongo,
    TransactionUpdateMongo,
    TransactionFilter
)

logger = logging.getLogger(__name__)


class TransactionMongoService:
    """Сервис для работы с транзакциями в MongoDB"""
    
    def __init__(self):
        self._collection = None
    
    @property
    def collection(self):
        """Получение коллекции транзакций с ленивой инициализацией"""
        if self._collection is None:
            from planning_service.database.mongodb import mongodb
            if mongodb.is_connected():
                self._collection = mongodb.transactions_collection
            else:
                raise Exception("MongoDB not connected")
        return self._collection
    
    async def create_transaction(self, transaction_data: TransactionCreateMongo) -> Optional[TransactionMongo]:
        """Создание новой транзакции"""
        try:
            # Создаем документ для вставки
            transaction_dict = transaction_data.model_dump()
            transaction_dict["created_at"] = datetime.utcnow()
            
            # Вставляем в MongoDB
            result = self.collection.insert_one(transaction_dict)
            
            # Получаем созданный документ
            created_doc = self.collection.find_one({"_id": result.inserted_id})
            
            if created_doc:
                return TransactionMongo.from_mongo(created_doc)
            
            return None
            
        except PyMongoError as e:
            logger.error(f"Error creating transaction: {e}")
            return None
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")
            return None
    
    async def get_transaction_by_id(self, transaction_id: str, user_id: str) -> Optional[TransactionMongo]:
        """Получение транзакции по ID"""
        try:
            object_id = ObjectId(transaction_id)
            doc = self.collection.find_one({
                "_id": object_id,
                "user_id": user_id
            })
            
            if doc:
                return TransactionMongo.from_mongo(doc)
            return None
            
        except Exception as e:
            logger.error(f"Error getting transaction by id {transaction_id}: {e}")
            return None
    
    async def get_transactions(
        self,
        user_id: str,
        filters: Optional[TransactionFilter] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TransactionMongo]:
        """Получение списка транзакций с фильтрацией"""
        try:
            # Базовый фильтр по пользователю
            query = {"user_id": user_id}
            
            # Добавляем дополнительные фильтры
            if filters:
                if filters.plan_id is not None:
                    query["plan_id"] = filters.plan_id
                
                if filters.type is not None:
                    query["type"] = filters.type
                
                if filters.category is not None:
                    query["category"] = filters.category
                
                # Фильтры по сумме
                amount_filter = {}
                if filters.min_amount is not None:
                    amount_filter["$gte"] = filters.min_amount
                if filters.max_amount is not None:
                    amount_filter["$lte"] = filters.max_amount
                if amount_filter:
                    query["amount"] = amount_filter
                
                # Фильтры по дате
                date_filter = {}
                if filters.start_date is not None:
                    date_filter["$gte"] = filters.start_date
                if filters.end_date is not None:
                    date_filter["$lte"] = filters.end_date
                if date_filter:
                    query["created_at"] = date_filter
            
            # Выполняем запрос с пагинацией и сортировкой
            cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
            
            transactions = []
            for doc in cursor:
                transaction = TransactionMongo.from_mongo(doc)
                if transaction:
                    transactions.append(transaction)
            
            return transactions
            
        except PyMongoError as e:
            logger.error(f"Error getting transactions: {e}")
            return []
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")
            return []
    
    async def update_transaction(
        self,
        transaction_id: str,
        user_id: str,
        update_data: TransactionUpdateMongo
    ) -> Optional[TransactionMongo]:
        """Обновление транзакции"""
        try:
            object_id = ObjectId(transaction_id)
            
            # Подготавливаем данные для обновления
            update_dict = update_data.model_dump(exclude_unset=True)
            
            if not update_dict:
                # Если нечего обновлять, возвращаем текущую транзакцию
                return await self.get_transaction_by_id(transaction_id, user_id)
            
            # Обновляем документ
            result = self.collection.update_one(
                {"_id": object_id, "user_id": user_id},
                {"$set": update_dict}
            )
            
            if result.modified_count > 0:
                return await self.get_transaction_by_id(transaction_id, user_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating transaction {transaction_id}: {e}")
            return None
    
    async def delete_transaction(self, transaction_id: str, user_id: str) -> bool:
        """Удаление транзакции"""
        try:
            object_id = ObjectId(transaction_id)
            
            result = self.collection.delete_one({
                "_id": object_id,
                "user_id": user_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting transaction {transaction_id}: {e}")
            return False
    
    async def get_transactions_by_plan(self, plan_id: int, user_id: str) -> List[TransactionMongo]:
        """Получение всех транзакций для конкретного плана"""
        filters = TransactionFilter(plan_id=plan_id, user_id=user_id)
        return await self.get_transactions(user_id, filters, limit=1000)
    
    async def get_plan_analytics(self, plan_id: int, user_id: str) -> dict:
        """Получение аналитики по плану"""
        try:
            pipeline = [
                {"$match": {"plan_id": plan_id, "user_id": user_id}},
                {
                    "$group": {
                        "_id": "$type",
                        "total_amount": {"$sum": "$amount"},
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            results = list(self.collection.aggregate(pipeline))
            
            analytics = {
                "plan_id": plan_id,
                "total_income": 0.0,
                "total_expenses": 0.0,
                "transaction_count": 0,
                "balance": 0.0
            }
            
            for result in results:
                transaction_type = result["_id"]
                total_amount = result["total_amount"]
                count = result["count"]
                
                analytics["transaction_count"] += count
                
                if transaction_type == "income":
                    analytics["total_income"] = total_amount
                elif transaction_type == "expense":
                    analytics["total_expenses"] = total_amount
            
            analytics["balance"] = analytics["total_income"] - analytics["total_expenses"]
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting plan analytics for plan {plan_id}: {e}")
            return {
                "plan_id": plan_id,
                "total_income": 0.0,
                "total_expenses": 0.0,
                "transaction_count": 0,
                "balance": 0.0
            }
    
    async def get_user_analytics(self, user_id: str) -> dict:
        """Получение общей аналитики пользователя"""
        try:
            pipeline = [
                {"$match": {"user_id": user_id}},
                {
                    "$group": {
                        "_id": "$type",
                        "total_amount": {"$sum": "$amount"},
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            results = list(self.collection.aggregate(pipeline))
            
            analytics = {
                "user_id": user_id,
                "total_income": 0.0,
                "total_expenses": 0.0,
                "transaction_count": 0,
                "balance": 0.0
            }
            
            for result in results:
                transaction_type = result["_id"]
                total_amount = result["total_amount"]
                count = result["count"]
                
                analytics["transaction_count"] += count
                
                if transaction_type == "income":
                    analytics["total_income"] = total_amount
                elif transaction_type == "expense":
                    analytics["total_expenses"] = total_amount
            
            analytics["balance"] = analytics["total_income"] - analytics["total_expenses"]
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting user analytics for user {user_id}: {e}")
            return {
                "user_id": user_id,
                "total_income": 0.0,
                "total_expenses": 0.0,
                "transaction_count": 0,
                "balance": 0.0
            }


# Глобальный экземпляр сервиса
transaction_mongo_service = TransactionMongoService() 