#!/usr/bin/env python3
"""
Скрипт для создания тестовых данных для нагрузочного тестирования
"""

import requests
import json
import sys
import time

# Конфигурация
API_GATEWAY_URL = "http://localhost:8000"
PLANNING_SERVICE_URL = "http://localhost:8081"

def get_token():
    """Получение JWT токена"""
    login_data = {
        "username": "admin",
        "password": "secret"
    }
    
    response = requests.post(f"{API_GATEWAY_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to get token: {response.status_code}")
        return None

def create_test_plans(token, count=50):
    """Создание тестовых планов"""
    headers = {"Authorization": f"Bearer {token}", "X-User": "admin"}
    
    created_plans = []
    for i in range(count):
        plan_data = {
            "title": f"Test Plan {i+1}",
            "description": f"This is test plan number {i+1} for performance testing",
            "planned_income": 5000.0 + (i * 100),
            "planned_expenses": 3000.0 + (i * 50)
        }
        
        response = requests.post(
            f"{PLANNING_SERVICE_URL}/plans",
            json=plan_data,
            headers=headers
        )
        
        if response.status_code == 200:
            plan = response.json()
            created_plans.append(plan)
            print(f"Created plan {i+1}: {plan['title']}")
        else:
            print(f"Failed to create plan {i+1}: {response.status_code}")
    
    return created_plans

def clear_cache(token):
    """Очистка кеша"""
    headers = {"Authorization": f"Bearer {token}", "X-User": "admin"}
    
    response = requests.post(f"{PLANNING_SERVICE_URL}/cache/clear", headers=headers)
    if response.status_code == 200:
        print("Cache cleared successfully")
    else:
        print(f"Failed to clear cache: {response.status_code}")

def main():
    print("Setting up test data...")
    
    # Получаем токен
    token = get_token()
    if not token:
        sys.exit(1)
    
    print(f"Got token: {token[:20]}...")
    
    # Очищаем кеш
    clear_cache(token)
    
    # Создаем тестовые планы
    plans = create_test_plans(token, count=20)
    print(f"Created {len(plans)} test plans")
    
    # Сохраняем информацию о созданных планах для дальнейшего использования
    test_data = {
        "token": token,
        "plans": plans,
        "created_at": time.time()
    }
    
    with open("test_data.json", "w") as f:
        json.dump(test_data, f, indent=2, default=str)
    
    print("Test data saved to test_data.json")

if __name__ == "__main__":
    main() 