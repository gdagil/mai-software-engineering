#!/usr/bin/env python3
"""
Тестирование MongoDB функциональности для Lab4
Запуск: python test_mongodb_example.py
"""

import requests
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
import logging
from dataclasses import dataclass

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TestConfig:
    """Конфигурация для тестов"""
    api_base: str = "http://localhost:8000"
    planning_service_base: str = "http://localhost:8081"
    username: str = "admin"
    password: str = "secret"
    headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {"Content-Type": "application/json"}

class APIClient:
    """Клиент для работы с API"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.token: Optional[str] = None
        self.auth_headers: Optional[Dict[str, str]] = None
    
    def authenticate(self) -> bool:
        """Аутентификация и получение токена"""
        login_data = {
            "username": self.config.username,
            "password": self.config.password
        }
        
        try:
            response = requests.post(
                f"{self.config.api_base}/auth/login",
                json=login_data,
                headers=self.config.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.auth_headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }
                logger.info("🔐 Аутентификация успешна!")
                return True
            else:
                logger.error(f"❌ Ошибка аутентификации: {response.status_code}")
                logger.error(response.text)
                return False
                
        except requests.RequestException as e:
            logger.error(f"❌ Ошибка подключения при аутентификации: {e}")
            return False
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Выполнение HTTP запроса с обработкой ошибок"""
        if not self.auth_headers and endpoint != "/auth/login":
            if not self.authenticate():
                raise Exception("Не удалось аутентифицироваться")
        
        url = f"{self.config.api_base}{endpoint}"
        headers = kwargs.pop('headers', self.auth_headers or self.config.headers)
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=30,
                **kwargs
            )
            return response
        except requests.RequestException as e:
            logger.error(f"❌ Ошибка запроса {method} {url}: {e}")
            raise

class MongoDBTester:
    """Класс для тестирования MongoDB функциональности"""
    
    def __init__(self, api_client: APIClient):
        self.api = api_client
        self.created_transactions: List[str] = []
    
    def create_test_transaction(self, transaction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Создание тестовой транзакции"""
        logger.info("📝 Создание транзакции в MongoDB...")
        
        response = self.api.make_request(
            "POST",
            "/api/transactions-mongo",
            json=transaction_data
        )
        
        if response.status_code == 200:
            created_transaction = response.json()
            transaction_id = created_transaction["_id"]
            self.created_transactions.append(transaction_id)
            
            logger.info(f"✅ Транзакция создана! ID: {transaction_id}")
            logger.info(f"   Сумма: {created_transaction['amount']} руб.")
            logger.info(f"   Категория: {created_transaction['category']}")
            return created_transaction
        else:
            logger.error(f"❌ Ошибка создания транзакции: {response.status_code}")
            logger.error(response.text)
            return None
    
    def get_all_transactions(self) -> Optional[List[Dict[str, Any]]]:
        """Получение всех транзакций"""
        logger.info("📋 Получение всех транзакций из MongoDB...")
        
        response = self.api.make_request("GET", "/api/transactions-mongo")
        
        if response.status_code == 200:
            transactions = response.json()
            logger.info(f"✅ Найдено транзакций: {len(transactions)}")
            
            # Показываем первые несколько транзакций
            for t in transactions[:3]:
                logger.info(f"   - {t['type']}: {t['amount']} руб. ({t['category']})")
            
            return transactions
        else:
            logger.error(f"❌ Ошибка получения транзакций: {response.status_code}")
            logger.error(response.text)
            return None
    
    def filter_transactions_by_category(self, category: str, limit: int = 5) -> Optional[List[Dict[str, Any]]]:
        """Фильтрация транзакций по категории"""
        logger.info(f"🔍 Фильтрация по категории '{category}'...")
        
        response = self.api.make_request(
            "GET",
            f"/api/transactions-mongo?category={category}&limit={limit}"
        )
        
        if response.status_code == 200:
            filtered_transactions = response.json()
            logger.info(f"✅ Найдено транзакций категории '{category}': {len(filtered_transactions)}")
            
            for t in filtered_transactions:
                logger.info(f"   - {t['description']}: {t['amount']} руб.")
            
            return filtered_transactions
        else:
            logger.error(f"❌ Ошибка фильтрации: {response.status_code}")
            logger.error(response.text)
            return None
    
    def update_transaction(self, transaction_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обновление транзакции"""
        logger.info(f"✏️ Обновление транзакции {transaction_id}...")
        
        response = self.api.make_request(
            "PUT",
            f"/api/transactions-mongo/{transaction_id}",
            json=update_data
        )
        
        if response.status_code == 200:
            updated_transaction = response.json()
            logger.info("✅ Транзакция обновлена!")
            logger.info(f"   Новая сумма: {updated_transaction['amount']} руб.")
            logger.info(f"   Новое описание: {updated_transaction['description']}")
            return updated_transaction
        else:
            logger.error(f"❌ Ошибка обновления: {response.status_code}")
            logger.error(response.text)
            return None
    
    def get_plan_analytics(self, plan_id: int) -> Optional[Dict[str, Any]]:
        """Получение аналитики по плану"""
        logger.info(f"📊 Аналитика по плану {plan_id}...")
        
        response = self.api.make_request(
            "GET",
            f"/api/transactions-mongo/plan/{plan_id}/analytics"
        )
        
        if response.status_code == 200:
            analytics = response.json()
            logger.info("✅ Аналитика получена!")
            logger.info(f"   Общий доход: {analytics['total_income']} руб.")
            logger.info(f"   Общие расходы: {analytics['total_expenses']} руб.")
            logger.info(f"   Баланс: {analytics['balance']} руб.")
            logger.info(f"   Количество транзакций: {analytics['transaction_count']}")
            return analytics
        else:
            logger.error(f"❌ Ошибка получения аналитики: {response.status_code}")
            logger.error(response.text)
            return None
    
    def run_full_test(self):
        """Выполнение полного тестирования MongoDB функциональности"""
        logger.info("🚀 Начало тестирования MongoDB функциональности...")
        
        # Тестовые данные
        transaction_data = {
            "plan_id": 1,
            "type": "expense",
            "amount": 150.0,
            "description": "Тестовая покупка продуктов",
            "category": "food",
            "user_id": "admin"
        }
        
        # 1. Создание транзакции
        created_transaction = self.create_test_transaction(transaction_data)
        if not created_transaction:
            return False
        
        transaction_id = created_transaction["_id"]
        
        # 2. Получение всех транзакций
        all_transactions = self.get_all_transactions()
        if all_transactions is None:
            return False
        
        # 3. Фильтрация по категории
        food_transactions = self.filter_transactions_by_category("food")
        if food_transactions is None:
            return False
        
        # 4. Обновление транзакции
        update_data = {
            "amount": 200.0,
            "description": "Обновленная покупка продуктов"
        }
        updated_transaction = self.update_transaction(transaction_id, update_data)
        if not updated_transaction:
            return False
        
        # 5. Аналитика по плану
        analytics = self.get_plan_analytics(1)
        if not analytics:
            return False
        
        # 6. Сравнение с PostgreSQL
        self.compare_with_postgresql(len(all_transactions))
        
        logger.info("🎉 Тестирование MongoDB функциональности завершено успешно!")
        return True
    
    def compare_with_postgresql(self, mongodb_count: int):
        """Сравнение с PostgreSQL транзакциями"""
        logger.info("🔄 Сравнение с PostgreSQL транзакциями...")
        
        try:
            response = self.api.make_request("GET", "/api/transactions")
            
            if response.status_code == 200:
                postgres_transactions = response.json()
                postgres_count = len(postgres_transactions)
                
                logger.info(f"📊 PostgreSQL транзакций: {postgres_count}")
                logger.info(f"📊 MongoDB транзакций: {mongodb_count}")
                logger.info(f"📊 Общее количество: {postgres_count + mongodb_count}")
            else:
                logger.error(f"❌ Ошибка получения PostgreSQL транзакций: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка при сравнении с PostgreSQL: {e}")

class HealthChecker:
    """Класс для проверки состояния сервисов"""
    
    def __init__(self, config: TestConfig):
        self.config = config
    
    def check_api_gateway(self) -> bool:
        """Проверка API Gateway"""
        try:
            response = requests.get(f"{self.config.api_base}/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ API Gateway: OK")
                return True
            else:
                logger.error("❌ API Gateway: Недоступен")
                return False
        except requests.RequestException as e:
            logger.error(f"❌ API Gateway: Ошибка подключения - {e}")
            return False
    
    def check_planning_service(self) -> bool:
        """Проверка Planning Service"""
        try:
            response = requests.get(f"{self.config.planning_service_base}/health", timeout=10)
            if response.status_code == 200:
                try:
                    health_data = response.json()
                    logger.info("✅ Planning Service: OK")
                    logger.info(f"   PostgreSQL: {health_data.get('database_mode', 'unknown')}")
                    logger.info(f"   MongoDB: {health_data.get('mongodb_status', 'unknown')}")
                except json.JSONDecodeError:
                    logger.info("✅ Planning Service: OK (простой ответ)")
                return True
            else:
                logger.error("❌ Planning Service: Недоступен")
                return False
        except requests.RequestException as e:
            logger.error(f"❌ Planning Service: Ошибка подключения - {e}")
            return False
    
    def check_database_health(self) -> Dict[str, str]:
        """Детальная проверка состояния БД"""
        try:
            response = requests.get(f"{self.config.planning_service_base}/db/health", timeout=10)
            if response.status_code == 200:
                try:
                    db_health = response.json()
                    logger.info("📊 Состояние БД:")
                    logger.info(f"   PostgreSQL: {db_health.get('postgresql', 'unknown')}")
                    logger.info(f"   MongoDB: {db_health.get('mongodb', 'unknown')}")
                    return db_health
                except json.JSONDecodeError:
                    logger.info("📊 Состояние БД: OK (простой ответ)")
                    return {"status": "ok"}
        except requests.RequestException as e:
            logger.error(f"❌ Ошибка проверки БД: {e}")
            return {"error": str(e)}
    
    def run_health_checks(self) -> bool:
        """Выполнение всех проверок состояния"""
        logger.info("🏥 Проверка состояния сервисов...")
        
        api_ok = self.check_api_gateway()
        planning_ok = self.check_planning_service()
        
        if api_ok and planning_ok:
            self.check_database_health()
            return True
        else:
            logger.error("❌ Один или несколько сервисов недоступны")
            return False

def main():
    """Основная функция запуска тестов"""
    logger.info("🚀 Запуск тестирования MongoDB функциональности...")
    logger.info("📋 Убедитесь, что сервисы запущены: docker-compose up")
    logger.info("=" * 60)
    
    # Инициализация
    config = TestConfig()
    health_checker = HealthChecker(config)
    
    # Проверка состояния сервисов
    if not health_checker.run_health_checks():
        logger.error("❌ Сервисы недоступны. Завершение тестирования.")
        return False
    
    logger.info("=" * 60)
    
    # Тестирование MongoDB
    api_client = APIClient(config)
    mongodb_tester = MongoDBTester(api_client)
    
    if not api_client.authenticate():
        logger.error("❌ Не удалось аутентифицироваться. Завершение тестирования.")
        return False
    
    success = mongodb_tester.run_full_test()
    
    if success:
        logger.info("🎉 Все тесты прошли успешно!")
    else:
        logger.error("❌ Некоторые тесты завершились с ошибками.")
    
    return success

if __name__ == "__main__":
    main() 