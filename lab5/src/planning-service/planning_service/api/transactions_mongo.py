from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from planning_service.models.mongodb_models import (
    TransactionMongo,
    TransactionCreateMongo,
    TransactionUpdateMongo,
    TransactionFilter,
    TransactionType
)
from planning_service.services.transaction_mongo_service import transaction_mongo_service
from planning_service.dependencies import get_current_user

router = APIRouter(prefix="/transactions-mongo", tags=["transactions-mongo"])


@router.get("", response_model=List[TransactionMongo])
async def get_transactions_mongo(
    current_user: str = Depends(get_current_user),
    plan_id: Optional[int] = Query(None, description="Filter by plan ID"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by transaction type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_amount: Optional[float] = Query(None, ge=0, description="Minimum amount filter"),
    max_amount: Optional[float] = Query(None, ge=0, description="Maximum amount filter"),
    start_date: Optional[datetime] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date filter (ISO format)"),
    skip: int = Query(0, ge=0, description="Number of transactions to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of transactions to return")
):
    """
    Get transactions from MongoDB with advanced filtering
    
    Retrieves transactions from MongoDB with support for multiple filters.
    
    **Query Parameters:**
    - `plan_id`: Filter by budget plan ID
    - `transaction_type`: Filter by transaction type (income/expense)
    - `category`: Filter by transaction category
    - `min_amount`: Minimum transaction amount
    - `max_amount`: Maximum transaction amount
    - `start_date`: Filter transactions after this date
    - `end_date`: Filter transactions before this date
    - `skip`: Pagination offset
    - `limit`: Number of results to return (max 1000)
    
    Example response:
    ```json
    [
        {
            "id": "507f1f77bcf86cd799439011",
            "plan_id": 1,
            "type": "expense",
            "amount": 150.0,
            "description": "Grocery shopping",
            "category": "food",
            "user_id": "admin",
            "created_at": "2024-01-15T14:30:00"
        }
    ]
    ```
    """
    filters = TransactionFilter(
        plan_id=plan_id,
        type=transaction_type,
        category=category,
        min_amount=min_amount,
        max_amount=max_amount,
        start_date=start_date,
        end_date=end_date,
        user_id=current_user
    )
    
    transactions = await transaction_mongo_service.get_transactions(
        user_id=current_user,
        filters=filters,
        skip=skip,
        limit=limit
    )
    
    return transactions


@router.post("", response_model=TransactionMongo)
async def create_transaction_mongo(
    transaction: TransactionCreateMongo,
    current_user: str = Depends(get_current_user)
):
    """
    Create a new transaction in MongoDB
    
    Creates a new transaction and stores it in MongoDB.
    
    Example request:
    ```json
    {
        "plan_id": 1,
        "type": "expense",
        "amount": 150.0,
        "description": "Grocery shopping",
        "category": "food",
        "user_id": "admin"
    }
    ```
    
    Example response:
    ```json
    {
        "id": "507f1f77bcf86cd799439011",
        "plan_id": 1,
        "type": "expense",
        "amount": 150.0,
        "description": "Grocery shopping",
        "category": "food",
        "user_id": "admin",
        "created_at": "2024-01-15T14:30:00Z"
    }
    ```
    """
    # Устанавливаем текущего пользователя
    transaction.user_id = current_user
    
    created_transaction = await transaction_mongo_service.create_transaction(transaction)
    
    if not created_transaction:
        raise HTTPException(status_code=500, detail="Failed to create transaction")
    
    return created_transaction


@router.get("/{transaction_id}", response_model=TransactionMongo)
async def get_transaction_mongo(
    transaction_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Get a specific transaction by MongoDB ObjectId
    
    **Path Parameters:**
    - `transaction_id`: MongoDB ObjectId of the transaction
    
    Example response:
    ```json
    {
        "id": "507f1f77bcf86cd799439011",
        "plan_id": 1,
        "type": "expense",
        "amount": 150.0,
        "description": "Grocery shopping",
        "category": "food",
        "user_id": "admin",
        "created_at": "2024-01-15T14:30:00Z"
    }
    ```
    """
    transaction = await transaction_mongo_service.get_transaction_by_id(transaction_id, current_user)
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return transaction


@router.put("/{transaction_id}", response_model=TransactionMongo)
async def update_transaction_mongo(
    transaction_id: str,
    update_data: TransactionUpdateMongo,
    current_user: str = Depends(get_current_user)
):
    """
    Update a transaction in MongoDB
    
    Updates an existing transaction. Only provided fields will be updated.
    
    Example request:
    ```json
    {
        "amount": 200.0,
        "description": "Updated grocery shopping",
        "category": "food"
    }
    ```
    
    Example response:
    ```json
    {
        "id": "507f1f77bcf86cd799439011",
        "plan_id": 1,
        "type": "expense",
        "amount": 200.0,
        "description": "Updated grocery shopping",
        "category": "food",
        "user_id": "admin",
        "created_at": "2024-01-15T14:30:00Z"
    }
    ```
    """
    updated_transaction = await transaction_mongo_service.update_transaction(
        transaction_id, current_user, update_data
    )
    
    if not updated_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found or update failed")
    
    return updated_transaction


@router.delete("/{transaction_id}")
async def delete_transaction_mongo(
    transaction_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Delete a transaction from MongoDB
    
    **Path Parameters:**
    - `transaction_id`: MongoDB ObjectId of the transaction to delete
    
    Example response:
    ```json
    {
        "message": "Transaction deleted successfully"
    }
    ```
    """
    success = await transaction_mongo_service.delete_transaction(transaction_id, current_user)
    
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return {"message": "Transaction deleted successfully"}


@router.get("/plan/{plan_id}/analytics")
async def get_plan_analytics_mongo(
    plan_id: int,
    current_user: str = Depends(get_current_user)
):
    """
    Get analytics for a specific plan from MongoDB transactions
    
    Calculates analytics based on MongoDB aggregation framework.
    
    **Path Parameters:**
    - `plan_id`: ID of the budget plan
    
    Example response:
    ```json
    {
        "plan_id": 1,
        "total_income": 5500.0,
        "total_expenses": 1630.0,
        "transaction_count": 8,
        "balance": 3870.0
    }
    ```
    """
    analytics = await transaction_mongo_service.get_plan_analytics(plan_id, current_user)
    return analytics


@router.get("/analytics/user")
async def get_user_analytics_mongo(
    current_user: str = Depends(get_current_user)
):
    """
    Get overall analytics for the current user from MongoDB
    
    Calculates total analytics across all plans for the user.
    
    Example response:
    ```json
    {
        "user_id": "admin",
        "total_income": 7500.0,
        "total_expenses": 1825.0,
        "transaction_count": 12,
        "balance": 5675.0
    }
    ```
    """
    analytics = await transaction_mongo_service.get_user_analytics(current_user)
    return analytics 