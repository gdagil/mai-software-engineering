from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from planning_service.models.pydantic_models import TransactionResponse, TransactionCreate
from planning_service.services import transactions_service
from planning_service.dependencies import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=List[TransactionResponse])
async def get_transactions(
    current_user: str = Depends(get_current_user),
    plan_id: Optional[int] = Query(None, description="Filter by plan ID")
):
    """
    Get all transactions for the current user
    
    Retrieves transactions owned by the authenticated user. 
    Optionally filter by plan_id to get transactions for a specific budget plan.
    
    **Query Parameters:**
    - `plan_id`: Optional. Filter transactions by budget plan ID
    
    Example response (all transactions):
    ```json
    [
        {
            "id": 1,
            "plan_id": 1,
            "type": "expense",
            "amount": 150.0,
            "description": "Grocery shopping",
            "category": "Food",
            "user_id": "admin",
            "created_at": "2024-01-15T14:30:00"
        },
        {
            "id": 2,
            "plan_id": 1,
            "type": "income",
            "amount": 2500.0,
            "description": "Salary",
            "category": "Work",
            "user_id": "admin",
            "created_at": "2024-01-15T08:00:00"
        }
    ]
    ```
    """
    transactions = await transactions_service.get_transactions(current_user, plan_id)
    return [TransactionResponse(**transaction) for transaction in transactions]


@router.post("", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: str = Depends(get_current_user)
):
    """
    Create a new transaction
    
    Creates a new income or expense transaction for a specific budget plan.
    Only the owner of the plan can add transactions to it.
    
    Example request:
    ```json
    {
        "plan_id": 1,
        "type": "expense",
        "amount": 150.0,
        "description": "Grocery shopping",
        "category": "Food"
    }
    ```
    
    Example response:
    ```json
    {
        "id": 1,
        "plan_id": 1,
        "type": "expense",
        "amount": 150.0,
        "description": "Grocery shopping",
        "category": "Food",
        "user_id": "admin",
        "created_at": "2024-01-15T14:30:00"
    }
    ```
    
    **Error Responses:**
    - `404`: Plan not found or access denied
    - `422`: Invalid transaction data (negative amount, invalid type, etc.)
    """
    try:
        created_transaction = await transactions_service.create_transaction(transaction, current_user)
        return TransactionResponse(**created_transaction)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: str = Depends(get_current_user)
):
    """
    Get a specific transaction by ID
    
    Retrieves a transaction by its ID. Only the owner can access the transaction.
    
    **Path Parameters:**
    - `transaction_id`: The unique identifier of the transaction
    
    Example response:
    ```json
    {
        "id": 1,
        "plan_id": 1,
        "type": "expense",
        "amount": 150.0,
        "description": "Grocery shopping",
        "category": "Food",
        "user_id": "admin",
        "created_at": "2024-01-15T14:30:00"
    }
    ```
    
    **Error Responses:**
    - `404`: Transaction not found or access denied
    """
    transaction = await transactions_service.get_transaction(transaction_id, current_user)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return TransactionResponse(**transaction)


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    current_user: str = Depends(get_current_user)
):
    """
    Delete a transaction
    
    Deletes an existing transaction. Only the owner can delete the transaction.
    This will affect the analytics calculations for the associated budget plan.
    
    **Path Parameters:**
    - `transaction_id`: The unique identifier of the transaction to delete
    
    Example response:
    ```json
    {
        "message": "Transaction deleted successfully"
    }
    ```
    
    **Error Responses:**
    - `404`: Transaction not found or access denied
    """
    success = await transactions_service.delete_transaction(transaction_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully"} 