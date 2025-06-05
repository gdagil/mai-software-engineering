from typing import List, Optional
from planning_service.database import database
from planning_service.models.database_models import BudgetPlanDB
from planning_service.models.pydantic_models import BudgetPlanCreate, BudgetPlanUpdate
from planning_service.config import settings
from datetime import datetime

in_memory_plans = {}
plan_counter = 1

async def get_plans(user_id: str) -> List[dict]:
    if settings.use_in_memory:
        user_plans = [plan for plan in in_memory_plans.values() if plan["user_id"] == user_id]
        return user_plans
    
    query = "SELECT * FROM budget_plans WHERE user_id = :user_id ORDER BY created_at DESC"
    return await database.fetch_all(query=query, values={"user_id": user_id})


async def create_plan(plan_data: BudgetPlanCreate, user_id: str) -> dict:
    global plan_counter
    
    if settings.use_in_memory:
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
    
    query = """
        INSERT INTO budget_plans (title, description, planned_income, planned_expenses, user_id, created_at, updated_at)
        VALUES (:title, :description, :planned_income, :planned_expenses, :user_id, :created_at, :updated_at)
        RETURNING *
    """
    values = {
        "title": plan_data.title,
        "description": plan_data.description,
        "planned_income": plan_data.planned_income,
        "planned_expenses": plan_data.planned_expenses,
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    return await database.fetch_one(query=query, values=values)


async def get_plan(plan_id: int, user_id: str) -> Optional[dict]:
    if settings.use_in_memory:
        plan = in_memory_plans.get(plan_id)
        if plan and plan["user_id"] == user_id:
            return plan
        return None
    
    query = "SELECT * FROM budget_plans WHERE id = :plan_id AND user_id = :user_id"
    return await database.fetch_one(query=query, values={"plan_id": plan_id, "user_id": user_id})


async def update_plan(plan_id: int, plan_data: BudgetPlanUpdate, user_id: str) -> Optional[dict]:
    existing_plan = await get_plan(plan_id, user_id)
    if not existing_plan:
        return None
    
    if settings.use_in_memory:
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
    
    update_fields = []
    values = {"plan_id": plan_id, "user_id": user_id, "updated_at": datetime.utcnow()}
    
    if plan_data.title is not None:
        update_fields.append("title = :title")
        values["title"] = plan_data.title
    if plan_data.description is not None:
        update_fields.append("description = :description")
        values["description"] = plan_data.description
    if plan_data.planned_income is not None:
        update_fields.append("planned_income = :planned_income")
        values["planned_income"] = plan_data.planned_income
    if plan_data.planned_expenses is not None:
        update_fields.append("planned_expenses = :planned_expenses")
        values["planned_expenses"] = plan_data.planned_expenses
    
    if not update_fields:
        return existing_plan
    
    update_fields.append("updated_at = :updated_at")
    
    query = f"""
        UPDATE budget_plans 
        SET {', '.join(update_fields)}
        WHERE id = :plan_id AND user_id = :user_id
        RETURNING *
    """
    
    return await database.fetch_one(query=query, values=values)


async def delete_plan(plan_id: int, user_id: str) -> bool:
    existing_plan = await get_plan(plan_id, user_id)
    if not existing_plan:
        return False
    
    if settings.use_in_memory:
        if plan_id in in_memory_plans:
            del in_memory_plans[plan_id]
        return True
    
    query = "DELETE FROM budget_plans WHERE id = :plan_id AND user_id = :user_id"
    await database.execute(query=query, values={"plan_id": plan_id, "user_id": user_id})
    return True 