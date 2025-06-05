from fastapi import APIRouter, Depends, HTTPException

from planning_service.models.pydantic_models import AnalyticsResponse
from planning_service.services import analytics_service
from planning_service.dependencies import get_current_user

router = APIRouter(prefix="/plans", tags=["analytics"])


@router.get("/{plan_id}/analytics", response_model=AnalyticsResponse)
async def get_plan_analytics(
    plan_id: int,
    current_user: str = Depends(get_current_user)
):
    """
    Get analytics for a specific budget plan
    
    Calculates and returns comprehensive analytics for a budget plan, including:
    - Total income and expenses from all transactions
    - Current balance (income - expenses)
    - Comparison with planned amounts
    - Variance percentages
    
    Only the owner of the plan can access its analytics.
    
    **Path Parameters:**
    - `plan_id`: The unique identifier of the budget plan
    
    Example response:
    ```json
    {
        "plan_id": 1,
        "total_income": 4800.0,
        "total_expenses": 3200.0,
        "balance": 1600.0,
        "planned_income": 5000.0,
        "planned_expenses": 3500.0,
        "income_vs_planned": -4.0,
        "expenses_vs_planned": -8.57
    }
    ```
    
    **Response Fields:**
    - `plan_id`: ID of the budget plan
    - `total_income`: Sum of all income transactions
    - `total_expenses`: Sum of all expense transactions  
    - `balance`: Current balance (total_income - total_expenses)
    - `planned_income`: Originally planned income amount
    - `planned_expenses`: Originally planned expenses amount
    - `income_vs_planned`: Percentage difference between actual and planned income
    - `expenses_vs_planned`: Percentage difference between actual and planned expenses
    
    **Error Responses:**
    - `404`: Plan not found or access denied
    """
    analytics = await analytics_service.get_plan_analytics(plan_id, current_user)
    if not analytics:
        raise HTTPException(status_code=404, detail="Plan not found")
    return analytics 