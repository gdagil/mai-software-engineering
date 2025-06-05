# Budget Planning System - Test Suite

This directory contains comprehensive tests for the Budget Planning System, covering both the API Gateway and Planning Service components.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_api_gateway.py      # API Gateway unit tests
├── test_planning_service.py # Planning Service unit tests
├── test_integration.py      # End-to-end integration tests
└── README.md               # This file
```

## Test Categories

### 1. Unit Tests
- **API Gateway Tests** (`test_api_gateway.py`)
  - Authentication endpoints
  - Proxy functionality
  - Error handling
  - Health checks

- **Planning Service Tests** (`test_planning_service.py`)
  - Budget plan CRUD operations
  - Transaction management
  - Analytics calculations
  - User authorization
  - Edge cases and validation

### 2. Integration Tests (`test_integration.py`)
- Complete workflow testing
- Service-to-service communication
- Authentication flow
- Data consistency
- Concurrent operations
- Error scenarios

## Running Tests

### Prerequisites
1. Ensure services are running:
   ```bash
   docker compose up -d
   ```

2. Install test dependencies:
   ```bash
   pip install pytest pytest-asyncio httpx
   ```

### Test Execution Options

#### Using the Test Runner Script
```bash
# Run all tests
python run_tests.py --all

# Run only unit tests
python run_tests.py --unit

# Run only integration tests
python run_tests.py --integration

# Run specific test categories
python run_tests.py --auth        # Authentication tests
python run_tests.py --api         # API endpoint tests
python run_tests.py --smoke       # Smoke tests

# Run specific test file
python run_tests.py --file api_gateway
python run_tests.py --file planning_service
python run_tests.py --file integration

# Run specific test function
python run_tests.py --function test_login_success

# Run with coverage report
python run_tests.py --all --coverage

# Run tests in parallel
python run_tests.py --all --parallel 4

# Verbose output
python run_tests.py --all --verbose
```

#### Using Pytest Directly
```bash
# Run all tests
pytest

# Run with markers
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m auth          # Authentication tests
pytest -m api           # API tests
pytest -m slow          # Slow running tests

# Run specific files
pytest tests/test_api_gateway.py
pytest tests/test_planning_service.py
pytest tests/test_integration.py

# Run specific test classes or functions
pytest tests/test_api_gateway.py::TestAuthentication
pytest tests/test_api_gateway.py::TestAuthentication::test_login_success

# Run with coverage
pytest --cov=api_gateway --cov=planning_service --cov-report=html

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run failed tests from last run
pytest --lf
```

## Test Fixtures

The test suite includes several useful fixtures defined in `conftest.py`:

- `services_ready`: Waits for services to be available
- `api_client`: HTTP client for making requests
- `auth_token`: Authentication token for protected endpoints
- `auth_headers`: Authorization headers
- `test_plan`: Creates and cleans up a test budget plan
- `test_transaction`: Creates and cleans up a test transaction
- `sample_plan_data`: Sample data for creating plans
- `sample_transaction_data`: Sample data for creating transactions

## Test Coverage

### API Gateway Tests
- ✅ Authentication (login, token validation, user info)
- ✅ Proxy endpoints (plans, transactions, analytics)
- ✅ Error handling (invalid requests, service unavailable)
- ✅ Authorization (protected endpoints)
- ✅ Health checks

### Planning Service Tests
- ✅ Budget Plans (CRUD operations, validation)
- ✅ Transactions (CRUD operations, filtering)
- ✅ Analytics (calculations, aggregations)
- ✅ User isolation (data access control)
- ✅ Error scenarios (invalid data, missing resources)
- ✅ Edge cases (large amounts, unicode text, zero values)

### Integration Tests
- ✅ Complete workflow (login → create plan → add transactions → analytics → cleanup)
- ✅ Service communication (API Gateway ↔ Planning Service)
- ✅ Authentication flow
- ✅ Data consistency
- ✅ Concurrent operations
- ✅ Error handling across services

## Test Data

Tests use realistic sample data:

### Sample Budget Plan
```json
{
    "title": "Monthly Budget",
    "description": "Personal monthly budget for 2024",
    "planned_income": 5000.0,
    "planned_expenses": 3500.0
}
```

### Sample Transaction
```json
{
    "plan_id": 1,
    "type": "expense",
    "amount": 150.0,
    "description": "Grocery shopping",
    "category": "Food"
}
```

### Sample User Credentials
```json
{
    "username": "admin",
    "password": "secret"
}
```

## Mocking Strategy

- **Unit Tests**: Mock external dependencies (database, HTTP clients)
- **Integration Tests**: Use real HTTP requests against running services
- **Service Layer**: Mock database operations for isolated testing
- **API Layer**: Mock service layer for endpoint testing

## Continuous Integration

The test suite is designed to work in CI/CD environments:

1. **Service Health Checks**: Tests wait for services to be ready
2. **Parallel Execution**: Tests can run in parallel for faster execution
3. **Markers**: Tests are categorized for selective execution
4. **Coverage Reports**: Generate coverage reports in multiple formats
5. **Clean Fixtures**: Automatic cleanup prevents test interference

## Debugging Tests

### Common Issues

1. **Services Not Ready**
   ```bash
   # Check if services are running
   docker compose ps
   
   # Check service logs
   docker compose logs api-gateway
   docker compose logs planning-service
   ```

2. **Authentication Failures**
   ```bash
   # Test login manually
   curl -X POST http://localhost:8000/auth/login \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "secret"}'
   ```

3. **Database Issues**
   ```bash
   # Check database connection
   docker compose logs postgres
   
   # Reset database
   docker compose down -v
   docker compose up -d
   ```

### Debug Mode
```bash
# Run tests with debug output
pytest -v -s

# Run specific test with debugging
pytest -v -s tests/test_api_gateway.py::TestAuthentication::test_login_success

# Use pdb for debugging
pytest --pdb
```

## Performance Testing

While not included in this test suite, consider adding:
- Load testing with `locust` or `artillery`
- Stress testing for concurrent users
- Database performance testing
- Memory usage monitoring

## Security Testing

Consider adding security-focused tests:
- SQL injection attempts
- XSS prevention
- Authentication bypass attempts
- Rate limiting tests
- Input validation edge cases

## Contributing

When adding new tests:

1. Follow the existing naming conventions
2. Add appropriate markers (`@pytest.mark.unit`, `@pytest.mark.integration`)
3. Include docstrings explaining what the test covers
4. Use fixtures for common setup/teardown
5. Mock external dependencies in unit tests
6. Add both positive and negative test cases
7. Update this README if adding new test categories 