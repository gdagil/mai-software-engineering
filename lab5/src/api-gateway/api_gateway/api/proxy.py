from fastapi import APIRouter, Depends, Request
from typing import Any, Optional

from api_gateway.dependencies import get_current_user
from api_gateway.services import proxy_service
from api_gateway.models.auth import UserResponse

router = APIRouter(prefix="/api", tags=["proxy"])


@router.get("/plans")
async def get_plans(current_user: UserResponse = Depends(get_current_user)):
    return await proxy_service.get_plans(current_user.username)


@router.post("/plans")
async def create_plan(plan_data: dict, current_user: UserResponse = Depends(get_current_user)):
    return await proxy_service.create_plan(current_user.username, plan_data)


@router.get("/plans/{plan_id}")
async def get_plan(plan_id: int, current_user: UserResponse = Depends(get_current_user)):
    return await proxy_service.get_plan(current_user.username, plan_id)


@router.put("/plans/{plan_id}")
async def update_plan(plan_id: int, plan_data: dict, current_user: UserResponse = Depends(get_current_user)):
    return await proxy_service.update_plan(current_user.username, plan_id, plan_data)


@router.delete("/plans/{plan_id}")
async def delete_plan(plan_id: int, current_user: UserResponse = Depends(get_current_user)):
    return await proxy_service.delete_plan(current_user.username, plan_id)


@router.get("/transactions")
async def get_transactions(current_user: UserResponse = Depends(get_current_user), plan_id: Optional[int] = None):
    return await proxy_service.get_transactions(current_user.username, plan_id)


@router.post("/transactions")
async def create_transaction(transaction_data: dict, current_user: UserResponse = Depends(get_current_user)):
    return await proxy_service.create_transaction(current_user.username, transaction_data)


@router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: int, current_user: UserResponse = Depends(get_current_user)):
    return await proxy_service.delete_transaction(current_user.username, transaction_id)


@router.get("/plans/{plan_id}/analytics")
async def get_plan_analytics(plan_id: int, current_user: UserResponse = Depends(get_current_user)):
    return await proxy_service.get_plan_analytics(current_user.username, plan_id)


# Простое проксирование для всех MongoDB endpoints
@router.api_route("/transactions-mongo/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_mongo_transactions(path: str, request: Request, current_user: UserResponse = Depends(get_current_user)):
    return await proxy_service.proxy_mongo_request(request, current_user.username, f"/transactions-mongo/{path}")


# Проксирование для корневого endpoint MongoDB транзакций
@router.api_route("/transactions-mongo", methods=["GET", "POST"])
async def proxy_mongo_transactions_root(request: Request, current_user: UserResponse = Depends(get_current_user)):
    return await proxy_service.proxy_mongo_request(request, current_user.username, "/transactions-mongo") 