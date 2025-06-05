import pytest
import httpx
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import json
from fastapi import HTTPException

from api_gateway.main import app
from api_gateway.models.auth import UserResponse

client = TestClient(app)


class TestAuthentication:
    """Test authentication endpoints"""

    def test_login_success(self):
        """Test successful login with valid credentials"""
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "secret"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "wrong_password"}
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_missing_fields(self):
        """Test login with missing fields"""
        response = client.post(
            "/auth/login",
            json={"username": "admin"}
        )
        assert response.status_code == 422

    def test_get_current_user_success(self):
        """Test getting current user info with valid token"""
        # First login to get token
        login_response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "secret"}
        )
        token = login_response.json()["access_token"]
        
        # Get user info
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert "id" in data
        assert "is_admin" in data

    def test_get_current_user_invalid_token(self):
        """Test getting user info with invalid token"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    def test_get_current_user_no_token(self):
        """Test getting user info without token"""
        response = client.get("/auth/me")
        assert response.status_code == 403


class TestProxyEndpoints:
    """Test proxy endpoints that forward requests to planning service"""

    @pytest.fixture
    def auth_headers(self):
        """Get authorization headers for authenticated requests"""
        login_response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "secret"}
        )
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @patch('api_gateway.services.proxy_service.proxy_request')
    def test_get_plans_success(self, mock_proxy, auth_headers):
        """Test getting plans through proxy"""
        mock_proxy.return_value = [
            {
                "id": 1,
                "title": "Test Plan",
                "planned_income": 1000.0,
                "planned_expenses": 800.0
            }
        ]
        
        response = client.get("/api/plans", headers=auth_headers)
        assert response.status_code == 200
        mock_proxy.assert_called_once()

    @patch('api_gateway.services.proxy_service.proxy_request')
    def test_create_plan_success(self, mock_proxy, auth_headers):
        """Test creating plan through proxy"""
        mock_proxy.return_value = {
            "id": 1,
            "title": "New Plan",
            "planned_income": 1500.0,
            "planned_expenses": 1200.0
        }
        
        plan_data = {
            "title": "New Plan",
            "description": "Test plan",
            "planned_income": 1500.0,
            "planned_expenses": 1200.0
        }
        
        response = client.post("/api/plans", json=plan_data, headers=auth_headers)
        assert response.status_code == 200
        mock_proxy.assert_called_once()

    @patch('api_gateway.services.proxy_service.proxy_request')
    def test_get_specific_plan(self, mock_proxy, auth_headers):
        """Test getting specific plan by ID"""
        mock_proxy.return_value = {
            "id": 1,
            "title": "Test Plan",
            "planned_income": 1000.0,
            "planned_expenses": 800.0
        }
        
        response = client.get("/api/plans/1", headers=auth_headers)
        assert response.status_code == 200
        mock_proxy.assert_called_once()

    @patch('api_gateway.services.proxy_service.proxy_request')
    def test_update_plan(self, mock_proxy, auth_headers):
        """Test updating plan through proxy"""
        mock_proxy.return_value = {
            "id": 1,
            "title": "Updated Plan",
            "planned_income": 2000.0,
            "planned_expenses": 1500.0
        }
        
        update_data = {
            "title": "Updated Plan",
            "planned_income": 2000.0
        }
        
        response = client.put("/api/plans/1", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        mock_proxy.assert_called_once()

    @patch('api_gateway.services.proxy_service.proxy_request')
    def test_get_transactions(self, mock_proxy, auth_headers):
        """Test getting transactions through proxy"""
        mock_proxy.return_value = [
            {
                "id": 1,
                "plan_id": 1,
                "type": "income",
                "amount": 500.0,
                "description": "Salary"
            }
        ]
        
        response = client.get("/api/transactions", headers=auth_headers)
        assert response.status_code == 200
        mock_proxy.assert_called_once()

    @patch('api_gateway.services.proxy_service.proxy_request')
    def test_create_transaction(self, mock_proxy, auth_headers):
        """Test creating transaction through proxy"""
        mock_proxy.return_value = {
            "id": 1,
            "plan_id": 1,
            "type": "expense",
            "amount": 100.0,
            "description": "Groceries"
        }
        
        transaction_data = {
            "plan_id": 1,
            "type": "expense",
            "amount": 100.0,
            "description": "Groceries",
            "category": "Food"
        }
        
        response = client.post("/api/transactions", json=transaction_data, headers=auth_headers)
        assert response.status_code == 200
        mock_proxy.assert_called_once()

    @patch('api_gateway.services.proxy_service.proxy_request')
    def test_get_analytics(self, mock_proxy, auth_headers):
        """Test getting plan analytics through proxy"""
        mock_proxy.return_value = {
            "plan_id": 1,
            "total_income": 1000.0,
            "total_expenses": 600.0,
            "balance": 400.0,
            "planned_income": 1500.0,
            "planned_expenses": 1200.0
        }
        
        response = client.get("/api/plans/1/analytics", headers=auth_headers)
        assert response.status_code == 200
        mock_proxy.assert_called_once()

    def test_unauthorized_access(self):
        """Test accessing protected endpoints without authentication"""
        endpoints = [
            "/api/plans",
            "/api/transactions",
            "/api/plans/1/analytics"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 403

    @patch('api_gateway.services.proxy_service.httpx.AsyncClient')
    def test_service_unavailable(self, mock_client, auth_headers):
        """Test handling of service unavailable scenarios"""
        mock_client.return_value.__aenter__.return_value.request.side_effect = httpx.RequestError("Connection failed")
        
        response = client.get("/api/plans", headers=auth_headers)
        assert response.status_code == 503
        assert "Service unavailable" in response.json()["detail"]


class TestErrorHandling:
    """Test error handling scenarios"""

    @pytest.fixture
    def auth_headers(self):
        login_response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "secret"}
        )
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_invalid_json_request(self, auth_headers):
        """Test handling of invalid JSON in request body"""
        response = client.post(
            "/api/plans",
            data="invalid json",
            headers={**auth_headers, "Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_missing_required_fields(self, auth_headers):
        """Test handling of missing required fields"""
        response = client.post(
            "/api/plans",
            json={"title": "Plan without required fields"},
            headers=auth_headers
        )
        # This should return 503 when the planning service returns an error
        assert response.status_code == 503

    def test_invalid_plan_id(self, auth_headers):
        """Test handling of invalid plan ID"""
        response = client.get("/api/plans/invalid_id", headers=auth_headers)
        assert response.status_code == 422

    @patch('api_gateway.services.proxy_service.proxy_request')
    def test_planning_service_error(self, mock_proxy, auth_headers):
        """Test handling of errors from planning service"""
        mock_proxy.side_effect = HTTPException(status_code=404, detail="Plan not found")
        
        response = client.get("/api/plans/999", headers=auth_headers)
        assert response.status_code == 404


class TestHealthCheck:
    """Test health check endpoint"""

    def test_health_check(self):
        """Test API Gateway health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "api-gateway" 