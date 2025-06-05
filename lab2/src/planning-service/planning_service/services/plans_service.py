from typing import List, Optional
from planning_service.models.pydantic_models import BudgetPlanCreate, BudgetPlanUpdate
from planning_service.config import settings
from datetime import datetime

in_memory_plans = {}
plan_counter = 1

async def get_plans(user_id: str) -> List[dict]:
    user_plans = [plan for plan in in_memory_plans.values() if plan["user_id"] == user_id]
    return user_plans


async def create_plan(plan_data: BudgetPlanCreate, user_id: str) -> dict:
    global plan_counter
    
    plan = {
        "id": plan_counter,
        "title": plan_data.title,
        "description": plan_data.description,
        "planned_income": plan_data.planned_income,
        "planned_expenses": plan_data.planned_expenses,
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    in_memory_plans[plan_counter] = plan
    plan_counter += 1
    return plan


async def get_plan(plan_id: int, user_id: str) -> Optional[dict]:
    plan = in_memory_plans.get(plan_id)
    if plan and plan["user_id"] == user_id:
        return plan
    return None


async def update_plan(plan_id: int, plan_data: BudgetPlanUpdate, user_id: str) -> Optional[dict]:
    existing_plan = await get_plan(plan_id, user_id)
    if not existing_plan:
        return None
    
    plan = in_memory_plans[plan_id]
    if plan_data.title is not None:
        plan["title"] = plan_data.title
    if plan_data.description is not None:
        plan["description"] = plan_data.description
    if plan_data.planned_income is not None:
        plan["planned_income"] = plan_data.planned_income
    if plan_data.planned_expenses is not None:
        plan["planned_expenses"] = plan_data.planned_expenses
    plan["updated_at"] = datetime.utcnow()
    return plan


async def delete_plan(plan_id: int, user_id: str) -> bool:
    existing_plan = await get_plan(plan_id, user_id)
    if not existing_plan:
        return False
    
    if plan_id in in_memory_plans:
        del in_memory_plans[plan_id]
    return True 