from typing import List, Optional
from planning_service.models.pydantic_models import TransactionCreate
from planning_service.config import settings
from planning_service.services.plans_service import get_plan
from datetime import datetime

in_memory_transactions = {}
transaction_counter = 1


async def get_transactions(user_id: str, plan_id: Optional[int] = None) -> List[dict]:
    user_transactions = [t for t in in_memory_transactions.values() if t["user_id"] == user_id]
    if plan_id:
        user_transactions = [t for t in user_transactions if t["plan_id"] == plan_id]
    return user_transactions


async def create_transaction(transaction_data: TransactionCreate, user_id: str) -> dict:
    global transaction_counter
    
    plan = await get_plan(transaction_data.plan_id, user_id)
    if not plan:
        raise ValueError("Plan not found or access denied")
    
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


async def get_transaction(transaction_id: int, user_id: str) -> Optional[dict]:
    transaction = in_memory_transactions.get(transaction_id)
    if transaction and transaction["user_id"] == user_id:
        return transaction
    return None


async def delete_transaction(transaction_id: int, user_id: str) -> bool:
    existing_transaction = await get_transaction(transaction_id, user_id)
    if not existing_transaction:
        return False
    
    if transaction_id in in_memory_transactions:
        del in_memory_transactions[transaction_id]
    return True


async def get_plan_transactions_summary(plan_id: int, username: str) -> dict:
    """Получить сводку по транзакциям плана"""
    plan_transactions = [t for t in in_memory_transactions.values() 
                        if t["plan_id"] == plan_id and t["user_id"] == username]
    
    total_income = sum(t["amount"] for t in plan_transactions if t["type"] == "income")
    total_expenses = sum(t["amount"] for t in plan_transactions if t["type"] == "expense")
    
    return {
        "income": float(total_income),
        "expenses": float(total_expenses)
    } 