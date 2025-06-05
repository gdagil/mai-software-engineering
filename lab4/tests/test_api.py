#!/usr/bin/env python3

import asyncio
import httpx
from typing import Optional


class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        
    async def login(self, username: str = "admin", password: str = "secret") -> bool:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/auth/login",
                    json={"username": username, "password": password}
                )
                if response.status_code == 200:
                    data = response.json()
                    self.token = data["access_token"]
                    print(f"Login successful. Token: {self.token[:20]}...")
                    return True
                else:
                    print(f"Login failed: {response.status_code}")
                    return False
            except Exception as e:
                print(f"Login error: {e}")
                return False
    
    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}
    
    async def get_user_info(self):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/auth/me",
                    headers=self.get_headers()
                )
                print(f"User info: {response.status_code}")
                if response.status_code == 200:
                    print(f"User data: {response.json()}")
                return response.status_code == 200
            except Exception as e:
                print(f"User info error: {e}")
                return False
    
    async def create_plan(self, title: str, planned_income: float, planned_expenses: float):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/plans",
                    json={
                        "title": title,
                        "planned_income": planned_income,
                        "planned_expenses": planned_expenses
                    },
                    headers=self.get_headers()
                )
                print(f"Create plan: {response.status_code}")
                if response.status_code == 200:
                    plan = response.json()
                    print(f"Created plan: {plan}")
                    return plan
                return None
            except Exception as e:
                print(f"Create plan error: {e}")
                return None
    
    async def get_plans(self):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/plans",
                    headers=self.get_headers()
                )
                print(f"Get plans: {response.status_code}")
                if response.status_code == 200:
                    plans = response.json()
                    print(f"Plans: {plans}")
                    return plans
                return None
            except Exception as e:
                print(f"Get plans error: {e}")
                return None
    
    async def create_transaction(self, plan_id: int, transaction_type: str, amount: float, description: str):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/transactions",
                    json={
                        "plan_id": plan_id,
                        "type": transaction_type,
                        "amount": amount,
                        "description": description
                    },
                    headers=self.get_headers()
                )
                print(f"Create transaction: {response.status_code}")
                if response.status_code == 200:
                    transaction = response.json()
                    print(f"Created transaction: {transaction}")
                    return transaction
                return None
            except Exception as e:
                print(f"Create transaction error: {e}")
                return None
    
    async def get_analytics(self, plan_id: int):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/plans/{plan_id}/analytics",
                    headers=self.get_headers()
                )
                print(f"Get analytics: {response.status_code}")
                if response.status_code == 200:
                    analytics = response.json()
                    print(f"Analytics: {analytics}")
                    return analytics
                return None
            except Exception as e:
                print(f"Get analytics error: {e}")
                return None


async def main():
    print("=== API Testing ===")
    
    tester = APITester("http://localhost:8000")
    
    success = await tester.login()
    if not success:
        print("Cannot continue without login")
        return
    
    await tester.get_user_info()
    
    plan = await tester.create_plan("Test Budget", 50000, 30000)
    if not plan:
        print("Cannot continue without plan")
        return
    
    await tester.get_plans()
    
    transaction = await tester.create_transaction(plan["id"], "income", 25000, "Salary")
    await tester.create_transaction(plan["id"], "expense", 5000, "Groceries")
    
    await tester.get_analytics(plan["id"])
    
    print("\n=== Direct service tests ===")
    
    planning_tester = APITester("http://localhost:8080")
    await planning_tester.get_plans()
    
    print("\n=== Testing completed ===")


if __name__ == "__main__":
    asyncio.run(main()) 