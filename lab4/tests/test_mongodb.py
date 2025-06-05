import pytest
import pytest_asyncio
import asyncio
import os
from datetime import datetime
from planning_service.database.mongodb import mongodb
from planning_service.models.mongodb_models import (
    TransactionMongo, 
    TransactionCreateMongo, 
    TransactionUpdateMongo,
    TransactionFilter,
    TransactionType
)
from planning_service.services.transaction_mongo_service import transaction_mongo_service


@pytest_asyncio.fixture(scope="module")
async def setup_mongodb():
    """Setup MongoDB connection for tests"""
    # Устанавливаем URL для тестового подключения
    original_mongodb_url = os.environ.get('MONGODB_URL')
    os.environ['MONGODB_URL'] = "mongodb://localhost:27017/test_transactions_db"
    
    # Переинициализируем подключение
    mongodb.disconnect()
    mongodb._client = None
    mongodb._database = None
    
    # Обеспечиваем подключение к MongoDB
    success = mongodb.connect()
    
    # Проверяем подключение
    if not success or not mongodb.is_connected():
        # Восстанавливаем исходную настройку
        if original_mongodb_url:
            os.environ['MONGODB_URL'] = original_mongodb_url
        else:
            os.environ.pop('MONGODB_URL', None)
        pytest.skip("MongoDB not available for tests")
    
    # Очищаем коллекцию перед тестами
    mongodb.transactions_collection.delete_many({})
    
    yield mongodb
    
    # Очищаем после тестов
    mongodb.transactions_collection.delete_many({})
    mongodb.disconnect()
    
    # Восстанавливаем исходную настройку
    if original_mongodb_url:
        os.environ['MONGODB_URL'] = original_mongodb_url
    else:
        os.environ.pop('MONGODB_URL', None)


class TestMongoDBConnection:
    """Тесты подключения к MongoDB"""
    
    @pytest.mark.asyncio
    async def test_mongodb_connection(self, setup_mongodb):
        """Тест подключения к MongoDB"""
        assert mongodb.is_connected()
        assert mongodb.database is not None
        assert mongodb.transactions_collection is not None


class TestTransactionMongoCRUD:
    """Тесты CRUD операций для транзакций в MongoDB"""
    
    @pytest.mark.asyncio
    async def test_create_transaction(self, setup_mongodb):
        """Тест создания транзакции"""
        transaction_data = TransactionCreateMongo(
            plan_id=1,
            type=TransactionType.expense,
            amount=150.0,
            description="Test grocery shopping",
            category="food",
            user_id="test_user"
        )
        
        created_transaction = await transaction_mongo_service.create_transaction(transaction_data)
        
        assert created_transaction is not None
        assert created_transaction.plan_id == 1
        assert created_transaction.type == TransactionType.expense
        assert created_transaction.amount == 150.0
        assert created_transaction.user_id == "test_user"
        assert created_transaction.id is not None
        assert created_transaction.created_at is not None
    
    @pytest.mark.asyncio
    async def test_get_transaction_by_id(self, setup_mongodb):
        """Тест получения транзакции по ID"""
        # Создаем транзакцию
        transaction_data = TransactionCreateMongo(
            plan_id=2,
            type=TransactionType.income,
            amount=2500.0,
            description="Test salary",
            category="salary",
            user_id="test_user"
        )
        
        created_transaction = await transaction_mongo_service.create_transaction(transaction_data)
        transaction_id = created_transaction.id
        
        # Получаем транзакцию
        retrieved_transaction = await transaction_mongo_service.get_transaction_by_id(transaction_id, "test_user")
        
        assert retrieved_transaction is not None
        assert retrieved_transaction.id == transaction_id
        assert retrieved_transaction.amount == 2500.0
        assert retrieved_transaction.type == TransactionType.income
    
    @pytest.mark.asyncio
    async def test_get_transaction_unauthorized(self, setup_mongodb):
        """Тест получения транзакции другим пользователем"""
        # Создаем транзакцию
        transaction_data = TransactionCreateMongo(
            plan_id=3,
            type=TransactionType.expense,
            amount=100.0,
            description="Test expense",
            category="test",
            user_id="user1"
        )
        
        created_transaction = await transaction_mongo_service.create_transaction(transaction_data)
        transaction_id = created_transaction.id
        
        # Пытаемся получить транзакцию другим пользователем
        retrieved_transaction = await transaction_mongo_service.get_transaction_by_id(transaction_id, "user2")
        
        assert retrieved_transaction is None
    
    @pytest.mark.asyncio
    async def test_update_transaction(self, setup_mongodb):
        """Тест обновления транзакции"""
        # Создаем транзакцию
        transaction_data = TransactionCreateMongo(
            plan_id=4,
            type=TransactionType.expense,
            amount=200.0,
            description="Original description",
            category="original",
            user_id="test_user"
        )
        
        created_transaction = await transaction_mongo_service.create_transaction(transaction_data)
        transaction_id = created_transaction.id
        
        # Обновляем транзакцию
        update_data = TransactionUpdateMongo(
            amount=250.0,
            description="Updated description",
            category="updated"
        )
        
        updated_transaction = await transaction_mongo_service.update_transaction(
            transaction_id, "test_user", update_data
        )
        
        assert updated_transaction is not None
        assert updated_transaction.amount == 250.0
        assert updated_transaction.description == "Updated description"
        assert updated_transaction.category == "updated"
        assert updated_transaction.type == TransactionType.expense  # Не изменилось
    
    @pytest.mark.asyncio
    async def test_delete_transaction(self, setup_mongodb):
        """Тест удаления транзакции"""
        # Создаем транзакцию
        transaction_data = TransactionCreateMongo(
            plan_id=5,
            type=TransactionType.income,
            amount=1000.0,
            description="To be deleted",
            category="test",
            user_id="test_user"
        )
        
        created_transaction = await transaction_mongo_service.create_transaction(transaction_data)
        transaction_id = created_transaction.id
        
        # Удаляем транзакцию
        success = await transaction_mongo_service.delete_transaction(transaction_id, "test_user")
        assert success is True
        
        # Проверяем, что транзакция удалена
        retrieved_transaction = await transaction_mongo_service.get_transaction_by_id(transaction_id, "test_user")
        assert retrieved_transaction is None


class TestTransactionFiltering:
    """Тесты фильтрации транзакций"""
    
    @pytest.mark.asyncio
    async def test_get_transactions_with_filters(self, setup_mongodb):
        """Тест получения транзакций с фильтрами"""
        # Очищаем коллекцию перед тестом
        mongodb.transactions_collection.delete_many({"user_id": "filter_user"})
        
        # Создаем несколько транзакций
        transactions_data = [
            TransactionCreateMongo(
                plan_id=1, type=TransactionType.income, amount=5000.0,
                description="Salary", category="salary", user_id="filter_user"
            ),
            TransactionCreateMongo(
                plan_id=1, type=TransactionType.expense, amount=1200.0,
                description="Rent", category="housing", user_id="filter_user"
            ),
            TransactionCreateMongo(
                plan_id=2, type=TransactionType.expense, amount=350.0,
                description="Groceries", category="food", user_id="filter_user"
            ),
            TransactionCreateMongo(
                plan_id=1, type=TransactionType.expense, amount=80.0,
                description="Gas", category="transportation", user_id="filter_user"
            )
        ]
        
        for transaction_data in transactions_data:
            await transaction_mongo_service.create_transaction(transaction_data)
        
        # Тест фильтра по плану
        plan1_transactions = await transaction_mongo_service.get_transactions(
            "filter_user", TransactionFilter(plan_id=1)
        )
        assert len(plan1_transactions) == 3
        
        # Тест фильтра по типу
        income_transactions = await transaction_mongo_service.get_transactions(
            "filter_user", TransactionFilter(type=TransactionType.income)
        )
        assert len(income_transactions) == 1
        assert income_transactions[0].type == TransactionType.income
        
        # Тест фильтра по сумме
        expensive_transactions = await transaction_mongo_service.get_transactions(
            "filter_user", TransactionFilter(min_amount=1000.0)
        )
        assert len(expensive_transactions) == 2  # Salary и Rent
        
        # Тест фильтра по категории
        food_transactions = await transaction_mongo_service.get_transactions(
            "filter_user", TransactionFilter(category="food")
        )
        assert len(food_transactions) == 1
        assert food_transactions[0].category == "food"


class TestTransactionAnalytics:
    """Тесты аналитики транзакций"""
    
    @pytest.mark.asyncio
    async def test_plan_analytics(self, setup_mongodb):
        """Тест аналитики по плану"""
        # Очищаем коллекцию перед тестом
        mongodb.transactions_collection.delete_many({"user_id": "analytics_user"})
        
        # Создаем транзакции для плана
        transactions_data = [
            TransactionCreateMongo(
                plan_id=10, type=TransactionType.income, amount=5000.0,
                description="Salary", category="salary", user_id="analytics_user"
            ),
            TransactionCreateMongo(
                plan_id=10, type=TransactionType.income, amount=500.0,
                description="Bonus", category="bonus", user_id="analytics_user"
            ),
            TransactionCreateMongo(
                plan_id=10, type=TransactionType.expense, amount=1200.0,
                description="Rent", category="housing", user_id="analytics_user"
            ),
            TransactionCreateMongo(
                plan_id=10, type=TransactionType.expense, amount=350.0,
                description="Groceries", category="food", user_id="analytics_user"
            )
        ]
        
        for transaction_data in transactions_data:
            await transaction_mongo_service.create_transaction(transaction_data)
        
        # Получаем аналитику
        analytics = await transaction_mongo_service.get_plan_analytics(10, "analytics_user")
        
        assert analytics["plan_id"] == 10
        assert analytics["total_income"] == 5500.0
        assert analytics["total_expenses"] == 1550.0
        assert analytics["balance"] == 3950.0
        assert analytics["transaction_count"] == 4
    
    @pytest.mark.asyncio
    async def test_user_analytics(self, setup_mongodb):
        """Тест общей аналитики пользователя"""
        # Очищаем коллекцию перед тестом
        mongodb.transactions_collection.delete_many({"user_id": "user_analytics"})
        
        # Создаем транзакции для разных планов
        transactions_data = [
            TransactionCreateMongo(
                plan_id=20, type=TransactionType.income, amount=3000.0,
                description="Income 1", category="salary", user_id="user_analytics"
            ),
            TransactionCreateMongo(
                plan_id=21, type=TransactionType.income, amount=2000.0,
                description="Income 2", category="freelance", user_id="user_analytics"
            ),
            TransactionCreateMongo(
                plan_id=20, type=TransactionType.expense, amount=800.0,
                description="Expense 1", category="housing", user_id="user_analytics"
            ),
            TransactionCreateMongo(
                plan_id=21, type=TransactionType.expense, amount=300.0,
                description="Expense 2", category="food", user_id="user_analytics"
            )
        ]
        
        for transaction_data in transactions_data:
            await transaction_mongo_service.create_transaction(transaction_data)
        
        # Получаем общую аналитику
        analytics = await transaction_mongo_service.get_user_analytics("user_analytics")
        
        assert analytics["user_id"] == "user_analytics"
        assert analytics["total_income"] == 5000.0
        assert analytics["total_expenses"] == 1100.0
        assert analytics["balance"] == 3900.0
        assert analytics["transaction_count"] == 4


class TestMongoDBModels:
    """Тесты MongoDB моделей"""
    
    def test_transaction_mongo_model(self):
        """Тест модели TransactionMongo"""
        # Тест создания модели
        transaction = TransactionMongo(
            plan_id=1,
            type=TransactionType.expense,
            amount=150.0,
            description="Test transaction",
            category="test",
            user_id="test_user",
            created_at=datetime.utcnow()
        )
        
        assert transaction.plan_id == 1
        assert transaction.type == TransactionType.expense
        assert transaction.amount == 150.0
        assert transaction.user_id == "test_user"
    
    def test_transaction_to_mongo(self):
        """Тест преобразования в MongoDB документ"""
        transaction = TransactionMongo(
            plan_id=1,
            type=TransactionType.income,
            amount=500.0,
            description="Test income",
            category="test",
            user_id="test_user",
            created_at=datetime.utcnow()
        )
        
        mongo_doc = transaction.to_mongo()
        
        assert "plan_id" in mongo_doc
        assert "type" in mongo_doc
        assert "amount" in mongo_doc
        assert "user_id" in mongo_doc
        assert mongo_doc["plan_id"] == 1
        assert mongo_doc["type"] == "income"
    
    def test_transaction_from_mongo(self):
        """Тест создания модели из MongoDB документа"""
        mongo_doc = {
            "_id": "507f1f77bcf86cd799439011",
            "plan_id": 1,
            "type": "expense",
            "amount": 200.0,
            "description": "Test from mongo",
            "category": "test",
            "user_id": "test_user",
            "created_at": datetime.utcnow()
        }
        
        transaction = TransactionMongo.from_mongo(mongo_doc)
        
        assert transaction is not None
        assert transaction.id == "507f1f77bcf86cd799439011"
        assert transaction.plan_id == 1
        assert transaction.type == TransactionType.expense
        assert transaction.amount == 200.0 