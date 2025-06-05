from typing import List, Optional
from planning_service.database import database
from planning_service.models.database_models import BudgetPlanDB
from planning_service.models.pydantic_models import BudgetPlanCreate, BudgetPlanUpdate
from planning_service.config import settings
from planning_service.services.cache_service import cache_service
from datetime import datetime

in_memory_plans = {}
plan_counter = 1

async def _get_plans_from_db(user_id: str) -> List[dict]:
    """Получение планов из базы данных"""
    if settings.use_in_memory:
        user_plans = [plan for plan in in_memory_plans.values() if plan["user_id"] == user_id]
        return user_plans
    
    query = "SELECT * FROM budget_plans WHERE user_id = :user_id ORDER BY created_at DESC"
    result = await database.fetch_all(query=query, values={"user_id": user_id})
    return [dict(row) for row in result]

async def _get_plan_from_db(plan_id: int, user_id: str) -> Optional[dict]:
    """Получение плана из базы данных"""
    if settings.use_in_memory:
        plan = in_memory_plans.get(plan_id)
        if plan and plan["user_id"] == user_id:
            return plan
        return None
    
    query = "SELECT * FROM budget_plans WHERE id = :plan_id AND user_id = :user_id"
    result = await database.fetch_one(query=query, values={"plan_id": plan_id, "user_id": user_id})
    return dict(result) if result else None

async def _create_plan_in_db(plan_data: BudgetPlanCreate, user_id: str) -> dict:
    """Создание плана в базе данных"""
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
    
    result = await database.fetch_one(query=query, values=values)
    return dict(result) if result else None

async def _update_plan_in_db(plan_id: int, plan_data: BudgetPlanUpdate, user_id: str) -> Optional[dict]:
    """Обновление плана в базе данных"""
    existing_plan = await _get_plan_from_db(plan_id, user_id)
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
    
    result = await database.fetch_one(query=query, values=values)
    return dict(result) if result else None

async def _delete_plan_from_db(plan_id: int, user_id: str) -> bool:
    """Удаление плана из базы данных"""
    existing_plan = await _get_plan_from_db(plan_id, user_id)
    if not existing_plan:
        return False
    
    if settings.use_in_memory:
        if plan_id in in_memory_plans:
            del in_memory_plans[plan_id]
        return True
    
    query = "DELETE FROM budget_plans WHERE id = :plan_id AND user_id = :user_id"
    await database.execute(query=query, values={"plan_id": plan_id, "user_id": user_id})
    return True

# Публичные методы сервиса с кешированием

async def get_plans(user_id: str) -> List[dict]:
    """Получение всех планов пользователя с кешированием (сквозное чтение)"""
    cache_key = cache_service.make_user_plans_key(user_id)
    
    return await cache_service.read_through(
        cache_key=cache_key,
        fetch_function=_get_plans_from_db,
        user_id=user_id
    )

async def get_plan(plan_id: int, user_id: str) -> Optional[dict]:
    """Получение конкретного плана с кешированием (сквозное чтение)"""
    cache_key = cache_service.make_plan_key(plan_id, user_id)
    
    return await cache_service.read_through(
        cache_key=cache_key,
        fetch_function=_get_plan_from_db,
        plan_id=plan_id,
        user_id=user_id
    )

async def create_plan(plan_data: BudgetPlanCreate, user_id: str) -> dict:
    """Создание плана с кешированием (сквозная запись)"""
    # Создаем план в БД
    created_plan = await _create_plan_in_db(plan_data, user_id)
    
    if created_plan:
        # Инвалидируем кеш списка планов пользователя
        user_plans_key = cache_service.make_user_plans_key(user_id)
        await cache_service.invalidate(user_plans_key)
        
        # Кешируем новый план
        plan_key = cache_service.make_plan_key(created_plan["id"], user_id)
        await cache_service.write_behind(plan_key, created_plan)
    
    return created_plan

async def update_plan(plan_id: int, plan_data: BudgetPlanUpdate, user_id: str) -> Optional[dict]:
    """Обновление плана с кешированием (сквозная запись)"""
    cache_key = cache_service.make_plan_key(plan_id, user_id)
    
    updated_plan = await cache_service.write_through(
        cache_key=cache_key,
        write_function=_update_plan_in_db,
        data=plan_data,
        plan_id=plan_id,
        plan_data=plan_data,
        user_id=user_id
    )
    
    if updated_plan:
        # Инвалидируем кеш списка планов пользователя
        user_plans_key = cache_service.make_user_plans_key(user_id)
        await cache_service.invalidate(user_plans_key)
    
    return updated_plan

async def delete_plan(plan_id: int, user_id: str) -> bool:
    """Удаление плана с очисткой кеша"""
    # Удаляем из БД
    success = await _delete_plan_from_db(plan_id, user_id)
    
    if success:
        # Очищаем кеш
        plan_key = cache_service.make_plan_key(plan_id, user_id)
        user_plans_key = cache_service.make_user_plans_key(user_id)
        
        await cache_service.invalidate(plan_key)
        await cache_service.invalidate(user_plans_key)
    
    return success 