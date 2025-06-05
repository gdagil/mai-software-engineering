import pytest
import asyncio
import httpx
import time
from typing import Dict, Optional


class IntegrationTester:
    """Integration tester for the complete budget planning system"""
    
    def __init__(self, api_gateway_url: str = "http://localhost:8000", planning_service_url: str = "http://localhost:8080"):
        self.api_gateway_url = api_gateway_url
        self.planning_service_url = planning_service_url
        self.token: Optional[str] = None
        self.created_plan_id: Optional[int] = None
        self.created_transaction_ids: list = []

    async def wait_for_services(self, timeout: int = 30):
        """Wait for both services to be ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                async with httpx.AsyncClient() as client:
                    # Check API Gateway
                    gateway_response = await client.get(f"{self.api_gateway_url}/health", timeout=5)
                    # Check Planning Service  
                    planning_response = await client.get(f"{self.planning_service_url}/health", timeout=5)
                    
                    if gateway_response.status_code == 200 and planning_response.status_code == 200:
                        return True
            except (httpx.RequestError, httpx.TimeoutException):
                pass
            
            await asyncio.sleep(1)
        
        return False

    async def login(self, username: str = "admin", password: str = "secret") -> bool:
        """Login and get JWT token"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_gateway_url}/auth/login",
                    json={"username": username, "password": password},
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    self.token = data["access_token"]
                    return True
                return False
            except Exception:
                return False

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    async def test_complete_workflow(self) -> Dict[str, bool]:
        """Test the complete workflow from login to analytics"""
        results = {}
        
        # Step 1: Login
        results["login"] = await self.login()
        if not results["login"]:
            return results

        # Step 2: Get user info
        results["get_user_info"] = await self.test_get_user_info()

        # Step 3: Create a budget plan
        results["create_plan"] = await self.test_create_plan()
        
        # Step 4: Get plans
        results["get_plans"] = await self.test_get_plans()
        
        # Step 5: Get specific plan
        if self.created_plan_id:
            results["get_specific_plan"] = await self.test_get_specific_plan()
            
            # Step 6: Update plan
            results["update_plan"] = await self.test_update_plan()
            
            # Step 7: Create transactions
            results["create_income_transaction"] = await self.test_create_transaction("income", 3000.0, "Salary")
            results["create_expense_transaction"] = await self.test_create_transaction("expense", 1200.0, "Rent")
            
            # Step 8: Get transactions
            results["get_transactions"] = await self.test_get_transactions()
            
            # Step 9: Get analytics
            results["get_analytics"] = await self.test_get_analytics()
            
            # Step 10: Delete transactions
            results["delete_transactions"] = await self.test_delete_transactions()
            
            # Step 11: Delete plan
            results["delete_plan"] = await self.test_delete_plan()
        
        return results

    async def test_get_user_info(self) -> bool:
        """Test getting current user info"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.api_gateway_url}/auth/me",
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                return response.status_code == 200 and "username" in response.json()
            except Exception:
                return False

    async def test_create_plan(self) -> bool:
        """Test creating a budget plan"""
        plan_data = {
            "title": "Integration Test Budget",
            "description": "Test budget plan for integration testing",
            "planned_income": 5000.0,
            "planned_expenses": 3500.0
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_gateway_url}/api/plans",
                    json=plan_data,
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                if response.status_code == 200:
                    plan = response.json()
                    self.created_plan_id = plan["id"]
                    return True
                return False
            except Exception:
                return False

    async def test_get_plans(self) -> bool:
        """Test getting all plans"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.api_gateway_url}/api/plans",
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                return response.status_code == 200 and isinstance(response.json(), list)
            except Exception:
                return False

    async def test_get_specific_plan(self) -> bool:
        """Test getting a specific plan by ID"""
        if not self.created_plan_id:
            return False
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.api_gateway_url}/api/plans/{self.created_plan_id}",
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                return response.status_code == 200 and response.json()["id"] == self.created_plan_id
            except Exception:
                return False

    async def test_update_plan(self) -> bool:
        """Test updating a plan"""
        if not self.created_plan_id:
            return False
            
        update_data = {
            "title": "Updated Integration Test Budget",
            "planned_income": 6000.0
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(
                    f"{self.api_gateway_url}/api/plans/{self.created_plan_id}",
                    json=update_data,
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                return response.status_code == 200
            except Exception:
                return False

    async def test_create_transaction(self, transaction_type: str, amount: float, description: str) -> bool:
        """Test creating a transaction"""
        if not self.created_plan_id:
            return False
            
        transaction_data = {
            "plan_id": self.created_plan_id,
            "type": transaction_type,
            "amount": amount,
            "description": description,
            "category": "Test Category"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_gateway_url}/api/transactions",
                    json=transaction_data,
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                if response.status_code == 200:
                    transaction = response.json()
                    self.created_transaction_ids.append(transaction["id"])
                    return True
                return False
            except Exception:
                return False

    async def test_get_transactions(self) -> bool:
        """Test getting transactions"""
        async with httpx.AsyncClient() as client:
            try:
                # Get all transactions
                response = await client.get(
                    f"{self.api_gateway_url}/api/transactions",
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                if response.status_code != 200:
                    return False
                
                # Get transactions filtered by plan
                if self.created_plan_id:
                    response = await client.get(
                        f"{self.api_gateway_url}/api/transactions?plan_id={self.created_plan_id}",
                        headers=self.get_auth_headers(),
                        timeout=10
                    )
                    return response.status_code == 200
                    
                return True
            except Exception:
                return False

    async def test_get_analytics(self) -> bool:
        """Test getting plan analytics"""
        if not self.created_plan_id:
            return False
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.api_gateway_url}/api/plans/{self.created_plan_id}/analytics",
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                if response.status_code == 200:
                    analytics = response.json()
                    required_fields = ["plan_id", "total_income", "total_expenses", "balance"]
                    return all(field in analytics for field in required_fields)
                return False
            except Exception:
                return False

    async def test_delete_transactions(self) -> bool:
        """Test deleting transactions"""
        success_count = 0
        
        for transaction_id in self.created_transaction_ids:
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.delete(
                        f"{self.api_gateway_url}/api/transactions/{transaction_id}",
                        headers=self.get_auth_headers(),
                        timeout=10
                    )
                    if response.status_code == 200:
                        success_count += 1
                except Exception:
                    pass
        
        return success_count == len(self.created_transaction_ids)

    async def test_delete_plan(self) -> bool:
        """Test deleting a plan"""
        if not self.created_plan_id:
            return False
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(
                    f"{self.api_gateway_url}/api/plans/{self.created_plan_id}",
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                return response.status_code == 200
            except Exception:
                return False

    async def test_error_scenarios(self) -> Dict[str, bool]:
        """Test various error scenarios"""
        results = {}
        
        # Test unauthorized access
        results["unauthorized_access"] = await self.test_unauthorized_access()
        
        # Test invalid data
        results["invalid_plan_data"] = await self.test_invalid_plan_data()
        
        # Test nonexistent resources
        results["nonexistent_plan"] = await self.test_nonexistent_plan()
        
        return results

    async def test_unauthorized_access(self) -> bool:
        """Test accessing endpoints without authentication"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.api_gateway_url}/api/plans", timeout=5)
                return response.status_code == 403
            except Exception:
                return False

    async def test_invalid_plan_data(self) -> bool:
        """Test creating plan with invalid data"""
        invalid_data = {
            "title": "Invalid Plan"
            # Missing required fields
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_gateway_url}/api/plans",
                    json=invalid_data,
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                return response.status_code in [400, 422]
            except Exception:
                return False

    async def test_nonexistent_plan(self) -> bool:
        """Test accessing nonexistent plan"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.api_gateway_url}/api/plans/99999",
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                return response.status_code == 404
            except Exception:
                return False


@pytest.mark.asyncio
class TestIntegration:
    """Integration tests for the budget planning system"""

    async def test_services_are_running(self):
        """Test that both services are running and healthy"""
        tester = IntegrationTester()
        services_ready = await tester.wait_for_services()
        assert services_ready, "Services are not running or not ready"

    async def test_complete_workflow(self):
        """Test the complete workflow from login to cleanup"""
        tester = IntegrationTester()
        
        # Wait for services to be ready
        services_ready = await tester.wait_for_services()
        assert services_ready, "Services are not ready"
        
        # Run complete workflow
        results = await tester.test_complete_workflow()
        
        # Assert all steps passed
        for step, success in results.items():
            assert success, f"Step '{step}' failed"

    async def test_authentication_flow(self):
        """Test authentication flow specifically"""
        tester = IntegrationTester()
        
        services_ready = await tester.wait_for_services()
        assert services_ready
        
        # Test successful login
        login_success = await tester.login()
        assert login_success, "Login failed"
        
        # Test getting user info
        user_info_success = await tester.test_get_user_info()
        assert user_info_success, "Getting user info failed"

    async def test_plan_management_flow(self):
        """Test plan management flow"""
        tester = IntegrationTester()
        
        services_ready = await tester.wait_for_services()
        assert services_ready
        
        # Login first
        login_success = await tester.login()
        assert login_success
        
        # Create plan
        create_success = await tester.test_create_plan()
        assert create_success, "Creating plan failed"
        
        # Get plans
        get_plans_success = await tester.test_get_plans()
        assert get_plans_success, "Getting plans failed"
        
        # Get specific plan
        if tester.created_plan_id:
            get_plan_success = await tester.test_get_specific_plan()
            assert get_plan_success, "Getting specific plan failed"
            
            # Update plan
            update_success = await tester.test_update_plan()
            assert update_success, "Updating plan failed"
            
            # Clean up
            delete_success = await tester.test_delete_plan()
            assert delete_success, "Deleting plan failed"

    async def test_transaction_flow(self):
        """Test transaction management flow"""
        tester = IntegrationTester()
        
        services_ready = await tester.wait_for_services()
        assert services_ready
        
        # Setup: Login and create plan
        login_success = await tester.login()
        assert login_success
        
        create_plan_success = await tester.test_create_plan()
        assert create_plan_success
        
        # Test transactions
        if tester.created_plan_id:
            # Create income transaction
            income_success = await tester.test_create_transaction("income", 2000.0, "Test Income")
            assert income_success, "Creating income transaction failed"
            
            # Create expense transaction
            expense_success = await tester.test_create_transaction("expense", 800.0, "Test Expense")
            assert expense_success, "Creating expense transaction failed"
            
            # Get transactions
            get_transactions_success = await tester.test_get_transactions()
            assert get_transactions_success, "Getting transactions failed"
            
            # Clean up
            delete_transactions_success = await tester.test_delete_transactions()
            assert delete_transactions_success, "Deleting transactions failed"
            
            delete_plan_success = await tester.test_delete_plan()
            assert delete_plan_success, "Deleting plan failed"

    async def test_analytics_flow(self):
        """Test analytics functionality"""
        tester = IntegrationTester()
        
        services_ready = await tester.wait_for_services()
        assert services_ready
        
        # Setup: Login, create plan, and transactions
        login_success = await tester.login()
        assert login_success
        
        create_plan_success = await tester.test_create_plan()
        assert create_plan_success
        
        if tester.created_plan_id:
            # Create some transactions for analytics
            await tester.test_create_transaction("income", 3000.0, "Salary")
            await tester.test_create_transaction("expense", 1500.0, "Rent")
            
            # Test analytics
            analytics_success = await tester.test_get_analytics()
            assert analytics_success, "Getting analytics failed"
            
            # Clean up
            await tester.test_delete_transactions()
            await tester.test_delete_plan()

    async def test_error_scenarios(self):
        """Test error handling scenarios"""
        tester = IntegrationTester()
        
        services_ready = await tester.wait_for_services()
        assert services_ready
        
        # Login for authenticated tests
        await tester.login()
        
        # Test error scenarios
        error_results = await tester.test_error_scenarios()
        
        for scenario, success in error_results.items():
            assert success, f"Error scenario '{scenario}' did not behave as expected"

    async def test_concurrent_operations(self):
        """Test concurrent operations on the system"""
        tester1 = IntegrationTester()
        tester2 = IntegrationTester()
        
        services_ready = await tester1.wait_for_services()
        assert services_ready
        
        # Both users login concurrently
        login1_task = asyncio.create_task(tester1.login())
        login2_task = asyncio.create_task(tester2.login())
        
        login1_success, login2_success = await asyncio.gather(login1_task, login2_task)
        assert login1_success and login2_success
        
        # Both users create plans concurrently
        create1_task = asyncio.create_task(tester1.test_create_plan())
        create2_task = asyncio.create_task(tester2.test_create_plan())
        
        create1_success, create2_success = await asyncio.gather(create1_task, create2_task)
        assert create1_success and create2_success
        
        # Clean up
        if tester1.created_plan_id:
            await tester1.test_delete_plan()
        if tester2.created_plan_id:
            await tester2.test_delete_plan()


# Utility function to run integration tests
async def run_integration_tests():
    """Run all integration tests and return results"""
    test_class = TestIntegration()
    
    tests = [
        ("Services Running", test_class.test_services_are_running),
        ("Authentication Flow", test_class.test_authentication_flow),
        ("Plan Management", test_class.test_plan_management_flow),
        ("Transaction Management", test_class.test_transaction_flow),
        ("Analytics", test_class.test_analytics_flow),
        ("Error Scenarios", test_class.test_error_scenarios),
        ("Concurrent Operations", test_class.test_concurrent_operations),
        ("Complete Workflow", test_class.test_complete_workflow),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            await test_func()
            results[test_name] = "PASS"
        except Exception as e:
            results[test_name] = f"FAIL: {str(e)}"
    
    return results


if __name__ == "__main__":
    # Run integration tests directly
    async def main():
        print("Running Integration Tests...")
        results = await run_integration_tests()
        
        for test_name, result in results.items():
            print(f"{test_name}: {result}")
    
    asyncio.run(main()) 