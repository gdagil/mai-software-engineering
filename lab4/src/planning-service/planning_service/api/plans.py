from fastapi import APIRouter, Depends, HTTPException
from typing import List

from planning_service.models.pydantic_models import BudgetPlanResponse, BudgetPlanCreate, BudgetPlanUpdate
from planning_service.services import plans_service
from planning_service.dependencies import get_current_user

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("", response_model=List[BudgetPlanResponse])
async def get_plans(current_user: str = Depends(get_current_user)):
    """
    Get all budget plans for the current user
    
    Returns a list of budget plans owned by the authenticated user.
    
    Example response:
    ```json
    [
        {
            "id": 1,
            "title": "Monthly Budget",
            "description": "Personal monthly budget for 2024",
            "planned_income": 5000.0,
            "planned_expenses": 3500.0,
            "user_id": "admin",
            "created_at": "2024-01-15T10:30:00",
            "updated_at": "2024-01-15T10:30:00"
        }
    ]
    ```
    """
    plans = await plans_service.get_plans(current_user)
    return [BudgetPlanResponse(**plan) for plan in plans]


@router.post("", response_model=BudgetPlanResponse)
async def create_plan(
    plan: BudgetPlanCreate, 
    current_user: str = Depends(get_current_user)
):
    """
    Create a new budget plan
    
    Creates a new budget plan for the authenticated user.
    
    Example request:
    ```json
    {
        "title": "Monthly Budget",
        "description": "Personal monthly budget for 2024",
        "planned_income": 5000.0,
        "planned_expenses": 3500.0
    }
    ```
    
    Example response:
    ```json
    {
        "id": 1,
        "title": "Monthly Budget",
        "description": "Personal monthly budget for 2024",
        "planned_income": 5000.0,
        "planned_expenses": 3500.0,
        "user_id": "admin",
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00"
    }
    ```
    """
    created_plan = await plans_service.create_plan(plan, current_user)
    return BudgetPlanResponse(**created_plan)


@router.get("/{plan_id}", response_model=BudgetPlanResponse)
async def get_plan(
    plan_id: int, 
    current_user: str = Depends(get_current_user)
):
    """
    Get a specific budget plan by ID
    
    Retrieves a budget plan by its ID. Only the owner can access the plan.
    
    **Path Parameters:**
    - `plan_id`: The unique identifier of the budget plan
    
    Example response:
    ```json
    {
        "id": 1,
        "title": "Monthly Budget",
        "description": "Personal monthly budget for 2024",
        "planned_income": 5000.0,
        "planned_expenses": 3500.0,
        "user_id": "admin",
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00"
    }
    ```
    
    **Error Responses:**
    - `404`: Plan not found or access denied
    """
    plan = await plans_service.get_plan(plan_id, current_user)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return BudgetPlanResponse(**plan)


@router.put("/{plan_id}", response_model=BudgetPlanResponse)
async def update_plan(
    plan_id: int,
    plan_update: BudgetPlanUpdate,
    current_user: str = Depends(get_current_user)
):
    """
    Update a budget plan
    
    Updates an existing budget plan. Only the owner can update the plan.
    
    **Path Parameters:**
    - `plan_id`: The unique identifier of the budget plan to update
    
    Example request:
    ```json
    {
        "title": "Updated Budget Plan",
        "planned_income": 6000.0,
        "planned_expenses": 4000.0
    }
    ```
    
    Example response:
    ```json
    {
        "id": 1,
        "title": "Updated Budget Plan",
        "description": "Personal monthly budget for 2024",
        "planned_income": 6000.0,
        "planned_expenses": 4000.0,
        "user_id": "admin",
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T12:45:00"
    }
    ```
    
    **Error Responses:**
    - `404`: Plan not found or access denied
    """
    plan = await plans_service.update_plan(plan_id, plan_update, current_user)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return BudgetPlanResponse(**plan)


@router.delete("/{plan_id}")
async def delete_plan(
    plan_id: int,
    current_user: str = Depends(get_current_user)
):
    """
    Delete a budget plan
    
    Deletes an existing budget plan and all associated transactions. 
    Only the owner can delete the plan.
    
    **Path Parameters:**
    - `plan_id`: The unique identifier of the budget plan to delete
    
    Example response:
    ```json
    {
        "message": "Plan deleted successfully"
    }
    ```
    
    **Error Responses:**
    - `404`: Plan not found or access denied
    """
    success = await plans_service.delete_plan(plan_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"message": "Plan deleted successfully"} 