import httpx
from fastapi import HTTPException, Request
from typing import Any, Dict

from api_gateway.config import settings


async def proxy_request(
    method: str,
    endpoint: str,
    headers: Dict[str, str] = None,
    json_data: Dict[str, Any] = None,
    params: Dict[str, Any] = None
) -> Any:
    url = f"{settings.planning_service_url}{endpoint}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                params=params
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


async def proxy_mongo_request(request: Request, username: str, endpoint: str) -> Any:
    """Проксирование MongoDB запросов к planning-service"""
    url = f"{settings.planning_service_url}{endpoint}"
    
    # Получаем тело запроса
    body = None
    if request.method in ["POST", "PUT"]:
        body = await request.body()
    
    # Получаем query параметры
    query_params = dict(request.query_params)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=url,
                headers={"X-User": username},
                content=body,
                params=query_params
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


async def get_plans(username: str) -> Any:
    return await proxy_request(
        method="GET",
        endpoint="/plans",
        headers={"X-User": username}
    )


async def create_plan(username: str, plan_data: Dict[str, Any]) -> Any:
    return await proxy_request(
        method="POST",
        endpoint="/plans",
        headers={"X-User": username},
        json_data=plan_data
    )


async def get_plan(username: str, plan_id: int) -> Any:
    return await proxy_request(
        method="GET",
        endpoint=f"/plans/{plan_id}",
        headers={"X-User": username}
    )


async def update_plan(username: str, plan_id: int, plan_data: Dict[str, Any]) -> Any:
    return await proxy_request(
        method="PUT",
        endpoint=f"/plans/{plan_id}",
        headers={"X-User": username},
        json_data=plan_data
    )


async def delete_plan(username: str, plan_id: int) -> Any:
    return await proxy_request(
        method="DELETE",
        endpoint=f"/plans/{plan_id}",
        headers={"X-User": username}
    )


async def get_transactions(username: str, plan_id: int = None) -> Any:
    params = {"plan_id": plan_id} if plan_id else None
    return await proxy_request(
        method="GET",
        endpoint="/transactions",
        headers={"X-User": username},
        params=params
    )


async def create_transaction(username: str, transaction_data: Dict[str, Any]) -> Any:
    return await proxy_request(
        method="POST",
        endpoint="/transactions",
        headers={"X-User": username},
        json_data=transaction_data
    )


async def delete_transaction(username: str, transaction_id: int) -> Any:
    return await proxy_request(
        method="DELETE",
        endpoint=f"/transactions/{transaction_id}",
        headers={"X-User": username}
    )


async def get_plan_analytics(username: str, plan_id: int) -> Any:
    return await proxy_request(
        method="GET",
        endpoint=f"/plans/{plan_id}/analytics",
        headers={"X-User": username}
    ) 