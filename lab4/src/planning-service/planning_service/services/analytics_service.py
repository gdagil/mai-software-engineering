from typing import Optional
from planning_service.models.pydantic_models import AnalyticsResponse
from planning_service.services.plans_service import get_plan
from planning_service.services.transactions_service import get_transactions


async def get_plan_analytics(plan_id: int, user_id: str) -> Optional[AnalyticsResponse]:
    plan = await get_plan(plan_id, user_id)
    if not plan:
        return None
    
    transactions = await get_transactions(user_id, plan_id)
    
    total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
    total_expenses = sum(t["amount"] for t in transactions if t["type"] == "expense")
    balance = total_income - total_expenses
    
    planned_income = plan["planned_income"]
    planned_expenses = plan["planned_expenses"]
    
    income_vs_planned = (total_income / planned_income * 100) if planned_income > 0 else 0
    expenses_vs_planned = (total_expenses / planned_expenses * 100) if planned_expenses > 0 else 0
    
    return AnalyticsResponse(
        plan_id=plan_id,
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        planned_income=planned_income,
        planned_expenses=planned_expenses,
        income_vs_planned=income_vs_planned,
        expenses_vs_planned=expenses_vs_planned
    ) 