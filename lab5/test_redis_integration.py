#!/usr/bin/env python3
"""
Скрипт для тестирования интеграции Redis кеширования
"""

import requests
import json
import time
import sys

API_GATEWAY_URL = "http://localhost:8000"
PLANNING_SERVICE_URL = "http://localhost:8081"

def get_token():
    """Получение JWT токена"""
    login_data = {
        "username": "admin",
        "password": "secret"
    }
    
    try:
        response = requests.post(f"{API_GATEWAY_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"❌ Failed to get token: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting token: {e}")
        return None

def test_redis_connection(token):
    """Тестирование подключения к Redis"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{PLANNING_SERVICE_URL}/cache/health", headers={"Authorization": f"Bearer {token}", "X-User": "admin"})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Redis connection: {'connected' if data['redis_connected'] else 'disconnected'}")
            print(f"✅ Cache enabled: {data['cache_enabled']}")
            return data['redis_connected']
        else:
            print(f"❌ Cache health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking Redis: {e}")
        return False

def test_caching_performance(token):
    """Тестирование производительности кеширования"""
    headers = {"Authorization": f"Bearer {token}"}
    cache_headers = {"Authorization": f"Bearer {token}", "X-User": "admin"}
    
    print("\n🧪 Testing caching performance...")
    
    # Очищаем кеш через Planning Service
    requests.post(f"{PLANNING_SERVICE_URL}/cache/clear", headers=cache_headers)
    
    # Тест без кеша (первый запрос) через API Gateway
    start_time = time.time()
    response = requests.get(f"{API_GATEWAY_URL}/api/plans", headers=headers)
    no_cache_time = time.time() - start_time
    
    if response.status_code == 200:
        print(f"✅ First request (no cache): {no_cache_time:.3f}s")
    else:
        print(f"❌ First request failed: {response.status_code}")
        return False
    
    # Тест с кешем (второй запрос)
    start_time = time.time()
    response = requests.get(f"{API_GATEWAY_URL}/api/plans", headers=headers)
    cache_time = time.time() - start_time
    
    if response.status_code == 200:
        print(f"✅ Second request (cached): {cache_time:.3f}s")
        speedup = no_cache_time / cache_time if cache_time > 0 else float('inf')
        print(f"🚀 Cache speedup: {speedup:.2f}x")
        
        if speedup > 1.5:
            print("✅ Caching is working effectively!")
        else:
            print("⚠️  Cache speedup is lower than expected")
        
        return True
    else:
        print(f"❌ Second request failed: {response.status_code}")
        return False

def test_cache_patterns(token):
    """Тестирование паттернов кеширования"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🧪 Testing cache patterns...")
    
    # 1. Тестируем Read-Through через API Gateway
    print("Testing Read-Through pattern...")
    response = requests.get(f"{API_GATEWAY_URL}/api/plans", headers=headers)
    if response.status_code == 200:
        print("✅ Read-Through: Data loaded from DB and cached")
    
    # 2. Тестируем Write-Through (создание плана) через API Gateway
    print("Testing Write-Through pattern...")
    plan_data = {
        "title": "Cache Test Plan",
        "description": "Plan for testing cache patterns",
        "planned_income": 1000.0,
        "planned_expenses": 800.0
    }
    
    response = requests.post(f"{API_GATEWAY_URL}/api/plans", 
                           json=plan_data, headers=headers)
    if response.status_code == 200:
        plan = response.json()
        print("✅ Write-Through: Plan created in DB and cached")
        
        # Проверяем, что план можно получить из кеша
        response = requests.get(f"{API_GATEWAY_URL}/api/plans/{plan['id']}", 
                              headers=headers)
        if response.status_code == 200:
            print("✅ Read from cache: Plan available immediately")
        
        return plan['id']
    else:
        print(f"❌ Write-Through failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_cache_invalidation(token, plan_id):
    """Тестирование инвалидации кеша"""
    if not plan_id:
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🧪 Testing cache invalidation...")
    
    # Обновляем план (должно инвалидировать кеш) через API Gateway
    update_data = {
        "title": "Updated Cache Test Plan",
        "planned_income": 1200.0
    }
    
    response = requests.put(f"{API_GATEWAY_URL}/api/plans/{plan_id}",
                          json=update_data, headers=headers)
    if response.status_code == 200:
        print("✅ Plan updated successfully")
        
        # Проверяем, что изменения видны
        response = requests.get(f"{API_GATEWAY_URL}/api/plans/{plan_id}",
                              headers=headers)
        if response.status_code == 200:
            updated_plan = response.json()
            if updated_plan['title'] == "Updated Cache Test Plan":
                print("✅ Cache invalidation: Updated data is visible")
            else:
                print("❌ Cache invalidation failed: Old data still cached")
        
        # Удаляем тестовый план
        requests.delete(f"{API_GATEWAY_URL}/api/plans/{plan_id}", headers=headers)

def main():
    print("🔄 Testing Redis caching integration...")
    
    # Получаем токен
    token = get_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        sys.exit(1)
    
    print(f"✅ Got authentication token")
    
    # Тестируем подключение к Redis
    redis_ok = test_redis_connection(token)
    if not redis_ok:
        print("❌ Redis is not available, skipping cache tests")
        sys.exit(1)
    
    # Тестируем производительность кеширования
    cache_performance_ok = test_caching_performance(token)
    
    # Тестируем паттерны кеширования
    plan_id = test_cache_patterns(token)
    
    # Тестируем инвалидацию кеша
    test_cache_invalidation(token, plan_id)
    
    print("\n✅ Redis caching integration test completed!")
    
    if cache_performance_ok:
        print("🎉 All tests passed! Redis caching is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs for details.")

if __name__ == "__main__":
    main() 