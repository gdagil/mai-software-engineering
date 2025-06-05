import pytest
import asyncio
import httpx
import time
from typing import Generator, Dict


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def services_ready():
    """Wait for services to be ready before running tests"""
    api_gateway_url = "http://localhost:8000"
    planning_service_url = "http://localhost:8080"
    timeout = 30
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            async with httpx.AsyncClient() as client:
                # Check API Gateway
                gateway_response = await client.get(f"{api_gateway_url}/health", timeout=5)
                # Check Planning Service  
                planning_response = await client.get(f"{planning_service_url}/health", timeout=5)
                
                if gateway_response.status_code == 200 and planning_response.status_code == 200:
                    return True
        except (httpx.RequestError, httpx.TimeoutException):
            pass
        
        await asyncio.sleep(1)
    
    pytest.skip("Services are not ready for testing")


@pytest.fixture
async def api_client():
    """HTTP client for API requests"""
    async with httpx.AsyncClient() as client:
        yield client


@pytest.fixture
async def auth_token():
    """Get authentication token for testing"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/auth/login",
            json={"username": "admin", "password": "secret"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            pytest.fail("Failed to get authentication token")


@pytest.fixture
def auth_headers(auth_token):
    """Authorization headers for authenticated requests"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
async def test_plan(auth_headers):
    """Create a test plan for testing and clean up after"""
    plan_data = {
        "title": "Test Budget Plan",
        "description": "A test plan for pytest",
        "planned_income": 5000.0,
        "planned_expenses": 3000.0
    }
    
    async with httpx.AsyncClient() as client:
        # Create plan
        response = await client.post(
            "http://localhost:8000/api/plans",
            json=plan_data,
            headers=auth_headers,
            timeout=10
        )
        
        if response.status_code == 200:
            plan = response.json()
            yield plan
            
            # Cleanup: Delete plan
            try:
                await client.delete(
                    f"http://localhost:8000/api/plans/{plan['id']}",
                    headers=auth_headers,
                    timeout=10
                )
            except Exception:
                pass  # Ignore cleanup errors
        else:
            pytest.fail("Failed to create test plan")


@pytest.fixture
async def test_transaction(auth_headers, test_plan):
    """Create a test transaction for testing and clean up after"""
    transaction_data = {
        "plan_id": test_plan["id"],
        "type": "income",
        "amount": 2000.0,
        "description": "Test transaction",
        "category": "Testing"
    }
    
    async with httpx.AsyncClient() as client:
        # Create transaction
        response = await client.post(
            "http://localhost:8000/api/transactions",
            json=transaction_data,
            headers=auth_headers,
            timeout=10
        )
        
        if response.status_code == 200:
            transaction = response.json()
            yield transaction
            
            # Cleanup: Delete transaction
            try:
                await client.delete(
                    f"http://localhost:8000/api/transactions/{transaction['id']}",
                    headers=auth_headers,
                    timeout=10
                )
            except Exception:
                pass  # Ignore cleanup errors
        else:
            pytest.fail("Failed to create test transaction")


@pytest.fixture(scope="session")
def api_gateway_url():
    """API Gateway base URL"""
    return "http://localhost:8000"


@pytest.fixture(scope="session")
def planning_service_url():
    """Planning Service base URL"""
    return "http://localhost:8080"


@pytest.fixture
def test_user_credentials():
    """Test user credentials"""
    return {"username": "admin", "password": "secret"}


@pytest.fixture
def sample_plan_data():
    """Sample plan data for testing"""
    return {
        "title": "Monthly Budget",
        "description": "Test monthly budget plan",
        "planned_income": 4000.0,
        "planned_expenses": 2500.0
    }


@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing"""
    return {
        "type": "expense",
        "amount": 150.0,
        "description": "Groceries",
        "category": "Food"
    }


@pytest.fixture
def invalid_plan_data():
    """Invalid plan data for error testing"""
    return {
        "title": "Invalid Plan"
        # Missing required fields
    }


@pytest.fixture
def invalid_transaction_data():
    """Invalid transaction data for error testing"""
    return {
        "type": "invalid_type",
        "amount": "not_a_number",
        "description": "Invalid transaction"
    }


# Markers for different test categories
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "auth: mark test as authentication related"
    )
    config.addinivalue_line(
        "markers", "api: mark test as API endpoint test"
    )


# Custom pytest hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add integration marker to integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Add slow marker to integration tests
        if "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.slow)
        
        # Add auth marker to authentication tests
        if "auth" in item.name.lower() or "login" in item.name.lower():
            item.add_marker(pytest.mark.auth)
        
        # Add api marker to API tests
        if any(keyword in item.nodeid for keyword in ["api", "endpoint", "proxy"]):
            item.add_marker(pytest.mark.api)


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Automatically cleanup test data after each test"""
    yield
    # This runs after each test
    # Add any global cleanup logic here if needed
    pass 