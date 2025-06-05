from typing import List, Optional
from planning_service.database import database
from planning_service.models.pydantic_models import TransactionCreate
from planning_service.config import settings
from planning_service.services.plans_service import get_plan
from datetime import datetime

in_memory_transactions = {}
transaction_counter = 1


async def get_transactions(user_id: str, plan_id: Optional[int] = None) -> List[dict]:
    if settings.use_in_memory:
        user_transactions = [t for t in in_memory_transactions.values() if t["user_id"] == user_id]
        if plan_id:
            user_transactions = [t for t in user_transactions if t["plan_id"] == plan_id]
        return user_transactions
    
    if plan_id:
        query = "SELECT * FROM transactions WHERE user_id = :user_id AND plan_id = :plan_id ORDER BY created_at DESC"
        return await database.fetch_all(query=query, values={"user_id": user_id, "plan_id": plan_id})
    else:
        query = "SELECT * FROM transactions WHERE user_id = :user_id ORDER BY created_at DESC"
        return await database.fetch_all(query=query, values={"user_id": user_id})


async def create_transaction(transaction_data: TransactionCreate, user_id: str) -> dict:
    global transaction_counter
    
    plan = await get_plan(transaction_data.plan_id, user_id)
    if not plan:
        raise ValueError("Plan not found or access denied")
    
    if settings.use_in_memory:
        transaction = {
            "id": transaction_counter,
            "plan_id": transaction_data.plan_id,
            "type": transaction_data.type,
            "amount": transaction_data.amount,
            "description": transaction_data.description,
            "category": transaction_data.category,
            "user_id": user_id,
            "created_at": datetime.utcnow()
        }
        in_memory_transactions[transaction_counter] = transaction
        transaction_counter += 1
        return transaction
    
    query = """
        INSERT INTO transactions (plan_id, type, amount, description, category, user_id, created_at)
        VALUES (:plan_id, :type, :amount, :description, :category, :user_id, :created_at)
        RETURNING *
    """
    values = {
        "plan_id": transaction_data.plan_id,
        "type": transaction_data.type,
        "amount": transaction_data.amount,
        "description": transaction_data.description,
        "category": transaction_data.category,
        "user_id": user_id,
        "created_at": datetime.utcnow()
    }
    
    return await database.fetch_one(query=query, values=values)


async def get_transaction(transaction_id: int, user_id: str) -> Optional[dict]:
    if settings.use_in_memory:
        transaction = in_memory_transactions.get(transaction_id)
        if transaction and transaction["user_id"] == user_id:
            return transaction
        return None
    
    query = "SELECT * FROM transactions WHERE id = :transaction_id AND user_id = :user_id"
    return await database.fetch_one(query=query, values={"transaction_id": transaction_id, "user_id": user_id})


async def delete_transaction(transaction_id: int, user_id: str) -> bool:
    existing_transaction = await get_transaction(transaction_id, user_id)
    if not existing_transaction:
        return False
    
    if settings.use_in_memory:
        if transaction_id in in_memory_transactions:
            del in_memory_transactions[transaction_id]
        return True
    
    query = "DELETE FROM transactions WHERE id = :transaction_id AND user_id = :user_id"
    await database.execute(query=query, values={"transaction_id": transaction_id, "user_id": user_id})
    return True


async def get_plan_transactions_summary(plan_id: int, username: str) -> dict:
    """Получить сводку по транзакциям плана"""
    if settings.use_in_memory:
        return {"income": 0.0, "expenses": 0.0}
    
    query = """
        SELECT 
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expenses
        FROM transactions 
        WHERE plan_id = :plan_id AND owner = :owner
    """
    
    row = await database.fetch_one(
        query=query, 
        values={"plan_id": plan_id, "owner": username}
    )
    
    return {
        "income": float(row["total_income"] or 0),
        "expenses": float(row["total_expenses"] or 0)
    } 