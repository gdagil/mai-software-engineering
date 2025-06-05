## Лабораторная работа №4
|              **Студент** | **Группа**   | **Вариант**  |
|--------------------------|--------------|--------------|
| Гудынин Данила Денисович | М8О-109СВ-24 | 12           |

## Описание проекта

Система бюджетирования с гибридным хранением данных, состоящая из двух микросервисов:
- **API Gateway** - управление аутентификацией и маршрутизацией запросов
- **Planning Service** - бизнес-логика с хранением в PostgreSQL (пользователи, планы) и MongoDB (транзакции)

### Архитектура

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Client/User   │───▶│   API Gateway    │───▶│ Planning Service │───▶│   PostgreSQL     │
│                 │    │  (Port: 8000)    │    │  (Port: 8080)    │    │  (Port: 5432)    │
│                 │    │                  │    │                  │    │                  │
│ • Authentication│    │ • JWT Auth       │    │ • Business Logic │    │ • Users & Plans  │
│ • API Requests  │    │ • Request Proxy  │    │ • CRUD Operations│    │ • Persistent     │
│                 │    │ • Token Validate │    │ • SQLAlchemy ORM │    │   Data Storage   │
│                 │    │                  │    │ • Data Validation│    │ • Indexed Tables │
└─────────────────┘    └──────────────────┘    └──────────────────┘    └──────────────────┘
                                                         │
                                                         ▼
                                                ┌──────────────────┐
                                                │     MongoDB      │
                                                │  (Port: 27017)   │
                                                │                  │
                                                │ • Transactions   │
                                                │ • NoSQL Storage  │
                                                │ • PyMongo Driver │
                                                │ • Indexed Fields │
                                                └──────────────────┘
```

## Требования к системе

### Обязательные требования
- [x] HTTP REST API для двух сервисов
- [x] JWT токен аутентификация (Bearer)
- [x] Отдельный endpoint для получения токена
- [x] GET/POST/PUT/DELETE методы
- [x] **Долговременное хранилище в PostgreSQL 14** (пользователи, планы)
- [x] **Долговременное хранилище в MongoDB 4.0** (транзакции)
- [x] **Скрипты создания БД и наполнения тестовыми данными**
- [x] **CRUD операции для всех сущностей в обеих БД**
- [x] **Хеширование паролей пользователей**
- [x] **Индексирование полей для поиска в PostgreSQL и MongoDB**
- [x] Мастер-пользователь (admin/secret)
- [x] OpenAPI спецификация
- [x] Docker Compose запуск

### Технический стек
- **Backend**: Python 3.11, FastAPI
- **ORM**: SQLAlchemy (PostgreSQL), PyMongo (MongoDB)
- **Databases**: PostgreSQL 14, MongoDB 4.0
- **Validation**: Pydantic
- **Authentication**: JWT Bearer tokens, bcrypt для хеширования
- **Containerization**: Docker, Docker Compose
- **Testing**: pytest, curl
- **Documentation**: OpenAPI/Swagger

## Структура баз данных

### PostgreSQL (Пользователи и планы)
- **users** - пользователи системы (логин, хешированный пароль)
- **budget_plans** - планы бюджета (название, описание, суммы, даты)

#### Индексы PostgreSQL
- `idx_users_username` - по логину пользователя
- `idx_plans_user_id` - по ID пользователя в планах
- `idx_plans_dates` - по датам планов

### MongoDB (Транзакции)
- **transactions** - коллекция транзакций (тип, сумма, категория, описание, план)

#### Индексы MongoDB
- `plan_id_1` - по ID плана
- `user_id_1` - по ID пользователя
- `type_1` - по типу транзакции (income/expense)
- `category_1` - по категории транзакции
- `created_at_1` - по дате создания
- `amount_1` - по сумме транзакции

## Быстрый старт

### 1. Клонирование и настройка

```bash
# Перейдите в директорию проекта
cd lab4

# Скопируйте файл конфигурации
cp env.example .env

# (Опционально) Отредактируйте переменные окружения
nano .env
```

### 2. Запуск через Docker Compose

```bash
# Сборка и запуск всех сервисов (PostgreSQL + MongoDB + сервисы)
make up
# или
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up --build -d
```

### 3. Проверка запуска

```bash
# Проверка здоровья сервисов
curl http://localhost:8000/health
curl http://localhost:8081/health

# Проверка подключения к БД
make test-db

# Проверка MongoDB функциональности
python test_mongodb_example.py

# Или используйте команду
make test-smoke
```

## Подробная инструкция по запуску

### Предварительные требования
- Docker и Docker Compose
- Python 3.11+ (для локального запуска)
- curl или Postman (для тестирования API)
- jq (для красивого вывода JSON, опционально)

### Шаг 1: Подготовка окружения

```bash
# Проверьте наличие необходимых инструментов
docker --version
docker-compose --version

# Проверьте настройки окружения
make env-check
```

### Шаг 2: Конфигурация баз данных

```bash
# Скопируйте пример конфигурации
cp env.example .env

# Основные настройки в .env:
# SECRET_KEY - секретный ключ для JWT
# DATABASE_URL - строка подключения к PostgreSQL
# MONGODB_URL - строка подключения к MongoDB
# POSTGRES_DB - имя базы данных PostgreSQL
# POSTGRES_USER - пользователь PostgreSQL
# POSTGRES_PASSWORD - пароль PostgreSQL
# PLANNING_SERVICE_URL - URL планирующего сервиса
# ACCESS_TOKEN_EXPIRE_MINUTES - время жизни токена
```

### Шаг 3: Сборка и запуск

```bash
# Сборка Docker образов
make build

# Запуск всех сервисов (PostgreSQL, MongoDB, API Gateway, Planning Service)
make up

# Просмотр логов
make logs

# Остановка сервисов
make down
```

### Шаг 4: Инициализация баз данных

```bash
# PostgreSQL автоматически инициализируется при первом запуске
# MongoDB автоматически создает коллекции и индексы при первом обращении

# Проверка состояния БД
curl http://localhost:8081/db/health

# Пересоздание БД (при необходимости)
make db-reset
```

### Шаг 5: Проверка работоспособности

```bash
# Проверка доступности сервисов
curl -f http://localhost:8000/health || echo "API Gateway недоступен"
curl -f http://localhost:8081/health || echo "Planning Service недоступен"

# Проверка MongoDB функциональности
python test_mongodb_example.py
```

## Работа с базами данных

### Подключение к PostgreSQL

```bash
# Через Docker Compose
docker-compose exec postgres psql -U budget_user -d budget_db

# Локально (если PostgreSQL установлен)
psql -h localhost -p 5432 -U budget_user -d budget_db
```

### Подключение к MongoDB

```bash
# Через Docker Compose
docker-compose exec mongodb mongo transactions_db

# Локально (если MongoDB установлен)
mongo mongodb://localhost:27017/transactions_db
```

### Скрипты инициализации

#### PostgreSQL
При первом запуске автоматически выполняются:
- Создание таблиц с индексами
- Вставка тестовых пользователей (включая admin/secret)
- Создание примеров планов бюджета

#### MongoDB
При первом обращении автоматически создаются:
- Коллекция транзакций
- Индексы для оптимизации запросов
- Схемы валидации данных

### CRUD операции

#### PostgreSQL (SQLAlchemy ORM):
- **Create**: Создание пользователей и планов с валидацией
- **Read**: Получение данных с фильтрацией и пагинацией
- **Update**: Обновление существующих записей
- **Delete**: Удаление записей с проверкой зависимостей

#### MongoDB (PyMongo):
- **Create**: Создание транзакций с автоматической валидацией
- **Read**: Получение транзакций с фильтрами и агрегацией
- **Update**: Обновление транзакций по ID
- **Delete**: Удаление транзакций с проверкой владельца

## Тестирование системы

### Автоматическое тестирование

```bash
# Запуск всех тестов
make test

# Только unit тесты
make test-unit

# Только интеграционные тесты
make test-integration

# Тесты базы данных
make test-db

# Smoke тесты (быстрая проверка)
make test-smoke

# API тесты через curl
make test-api

# Тестирование MongoDB функциональности
python test_mongodb_example.py
```

### Ручное тестирование API

#### 1. Получение JWT токена

```bash
# Запрос токена для администратора
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "secret"
  }'

# Ответ:
# {
#   "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
#   "token_type": "bearer"
# }
```

#### 2. Использование токена для запросов

```bash
# Сохраните токен в переменную (замените YOUR_TOKEN)
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Получение информации о пользователе
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/auth/me

# Получение планов бюджета из PostgreSQL
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/plans

# Получение транзакций из MongoDB
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/transactions-mongo
```

#### 3. Создание плана бюджета (PostgreSQL)

```bash
curl -X POST "http://localhost:8000/api/plans" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Месячный бюджет",
    "description": "План доходов и расходов на месяц",
    "planned_income": 100000,
    "planned_expenses": 80000,
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }'
```

#### 4. Создание транзакции в PostgreSQL

```bash
curl -X POST "http://localhost:8000/api/transactions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": 1,
    "type": "income",
    "amount": 50000,
    "description": "Зарплата",
    "category": "salary"
  }'
```

#### 5. Создание транзакции в MongoDB

```bash
curl -X POST "http://localhost:8000/api/transactions-mongo" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": 1,
    "type": "expense",
    "amount": 1500,
    "description": "Покупка продуктов",
    "category": "food",
    "user_id": "admin"
  }'
```

#### 6. Получение аналитики по плану (MongoDB)

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/transactions-mongo/plan/1/analytics
```

### Интерактивное тестирование

#### Swagger UI
Откройте в браузере:
- API Gateway: http://localhost:8000/docs
- Planning Service: http://localhost:8081/docs

#### Доступные пользователи
- **Администратор**: `admin` / `secret` (пароль хеширован в PostgreSQL)

## API Endpoints

### API Gateway (http://localhost:8000)

| Метод | Endpoint | Описание | Хранилище | Аутентификация |
|-------|----------|----------|-----------|----------------|
| POST | `/auth/login` | Получение JWT токена | PostgreSQL | Нет |
| POST | `/auth/register` | Регистрация пользователя | PostgreSQL | Нет |
| GET | `/auth/me` | Информация о пользователе | PostgreSQL | JWT |
| GET | `/api/plans` | Список планов бюджета | PostgreSQL | JWT |
| POST | `/api/plans` | Создание плана | PostgreSQL | JWT |
| GET | `/api/plans/{id}` | Получение плана по ID | PostgreSQL | JWT |
| PUT | `/api/plans/{id}` | Обновление плана | PostgreSQL | JWT |
| DELETE | `/api/plans/{id}` | Удаление плана | PostgreSQL | JWT |
| GET | `/api/transactions` | Список транзакций | PostgreSQL | JWT |
| POST | `/api/transactions` | Создание транзакции | PostgreSQL | JWT |
| GET | `/api/transactions/{id}` | Получение транзакции | PostgreSQL | JWT |
| PUT | `/api/transactions/{id}` | Обновление транзакции | PostgreSQL | JWT |
| DELETE | `/api/transactions/{id}` | Удаление транзакции | PostgreSQL | JWT |
| **GET** | **`/api/transactions-mongo`** | **Список транзакций** | **MongoDB** | **JWT** |
| **POST** | **`/api/transactions-mongo`** | **Создание транзакции** | **MongoDB** | **JWT** |
| **GET** | **`/api/transactions-mongo/{id}`** | **Получение транзакции** | **MongoDB** | **JWT** |
| **PUT** | **`/api/transactions-mongo/{id}`** | **Обновление транзакции** | **MongoDB** | **JWT** |
| **DELETE** | **`/api/transactions-mongo/{id}`** | **Удаление транзакции** | **MongoDB** | **JWT** |
| **GET** | **`/api/transactions-mongo/plan/{id}/analytics`** | **Аналитика по плану** | **MongoDB** | **JWT** |
| **GET** | **`/api/transactions-mongo/user/analytics`** | **Аналитика пользователя** | **MongoDB** | **JWT** |
| GET | `/health` | Проверка здоровья | - | Нет |

### Planning Service (http://localhost:8081)

| Метод | Endpoint | Описание | Хранилище | Аутентификация |
|-------|----------|----------|-----------|----------------|
| GET | `/plans` | Список планов | PostgreSQL | X-User Header |
| POST | `/plans` | Создание плана | PostgreSQL | X-User Header |
| GET | `/plans/{id}` | Получение плана | PostgreSQL | X-User Header |
| PUT | `/plans/{id}` | Обновление плана | PostgreSQL | X-User Header |
| DELETE | `/plans/{id}` | Удаление плана | PostgreSQL | X-User Header |
| GET | `/transactions` | Список транзакций | PostgreSQL | X-User Header |
| POST | `/transactions` | Создание транзакции | PostgreSQL | X-User Header |
| GET | `/transactions/{id}` | Получение транзакции | PostgreSQL | X-User Header |
| PUT | `/transactions/{id}` | Обновление транзакции | PostgreSQL | X-User Header |
| DELETE | `/transactions/{id}` | Удаление транзакции | PostgreSQL | X-User Header |
| **GET** | **`/transactions-mongo`** | **Список транзакций** | **MongoDB** | **X-User Header** |
| **POST** | **`/transactions-mongo`** | **Создание транзакции** | **MongoDB** | **X-User Header** |
| **GET** | **`/transactions-mongo/{id}`** | **Получение транзакции** | **MongoDB** | **X-User Header** |
| **PUT** | **`/transactions-mongo/{id}`** | **Обновление транзакции** | **MongoDB** | **X-User Header** |
| **DELETE** | **`/transactions-mongo/{id}`** | **Удаление транзакции** | **MongoDB** | **X-User Header** |
| **GET** | **`/transactions-mongo/plan/{id}/analytics`** | **Аналитика по плану** | **MongoDB** | **X-User Header** |
| **GET** | **`/transactions-mongo/user/analytics`** | **Аналитика пользователя** | **MongoDB** | **X-User Header** |
| GET | `/plans/{id}/analytics` | Аналитика по плану | PostgreSQL | X-User Header |
| GET | `/health` | Проверка здоровья | - | Нет |
| GET | `/db/health` | Проверка БД | PostgreSQL + MongoDB | Нет |

## Структура проекта

```
lab4/
├── README.md                    # Документация проекта
├── docker-compose.yml           # Конфигурация Docker Compose (PostgreSQL + MongoDB)
├── Makefile                     # Команды для управления проектом
├── env.example                  # Пример переменных окружения
├── .env                         # Переменные окружения (создается)
├── pytest.ini                  # Конфигурация pytest
├── test_mongodb_example.py      # Тестирование MongoDB функциональности
├── init-db/                     # Скрипты инициализации PostgreSQL
│   ├── 01-create-tables.sql     # Создание таблиц и индексов
│   └── 02-insert-data.sql       # Вставка тестовых данных
├── init-mongo/                  # Скрипты инициализации MongoDB
│   └── init-indexes.js          # Создание индексов в MongoDB
├── src/
│   ├── api-gateway/            # API Gateway сервис
│   │   ├── api_gateway/        # Исходный код
│   │   │   ├── models.py       # Pydantic модели
│   │   │   ├── auth.py         # JWT аутентификация
│   │   │   └── main.py         # FastAPI приложение
│   │   ├── Dockerfile          # Docker образ
│   │   ├── pyproject.toml      # Python зависимости
│   │   └── README.md           # Документация сервиса
│   └── planning-service/       # Planning Service
│       ├── planning_service/   # Исходный код
│       │   ├── database/       # Подключения к БД
│       │   │   ├── postgres.py # PostgreSQL подключение
│       │   │   └── mongodb.py  # MongoDB подключение
│       │   ├── models/         # Модели данных
│       │   │   ├── postgres_models.py    # SQLAlchemy модели
│       │   │   └── mongodb_models.py     # Pydantic модели для MongoDB
│       │   ├── services/       # Бизнес-логика
│       │   │   ├── plan_service.py       # Работа с планами (PostgreSQL)
│       │   │   ├── transaction_service.py # Работа с транзакциями (PostgreSQL)
│       │   │   └── transaction_mongo_service.py # Работа с транзакциями (MongoDB)
│       │   ├── config.py       # Конфигурация
│       │   └── main.py         # FastAPI приложение
│       ├── Dockerfile          # Docker образ
│       ├── pyproject.toml      # Python зависимости
│       └── README.md           # Документация сервиса
└── tests/                      # Тесты
    ├── test_api_gateway.py     # Тесты API Gateway
    ├── test_planning_service.py # Тесты Planning Service
    ├── test_database.py        # Тесты PostgreSQL
    ├── test_mongodb.py         # Тесты MongoDB
    ├── test_integration.py     # Интеграционные тесты
    └── conftest.py             # Конфигурация pytest
```

## Генерация OpenAPI спецификации

```bash
# Запустите сервисы
make up

# Сохраните OpenAPI спецификации
make save-openapi

# Файлы будут сохранены как:
# - openapi-api-gateway.json
# - openapi-planning-service.json
```

## Полезные команды

```bash
# Просмотр всех доступных команд
make help

# Проверка конфигурации
make env-check

# Работа с PostgreSQL
make db-connect      # Подключение к PostgreSQL
make db-status       # Статус PostgreSQL
make db-reset        # Пересоздание PostgreSQL

# Работа с MongoDB
docker-compose exec mongodb mongo transactions_db  # Подключение к MongoDB

# Очистка системы
make clean

# Перезапуск сервисов
make down && make up

# Просмотр логов конкретного сервиса
docker-compose logs -f api-gateway
docker-compose logs -f planning-service
docker-compose logs -f postgres
docker-compose logs -f mongodb
```

## Устранение неполадок

### Порты заняты
```bash
# Проверьте, что порты 8000, 8081, 5432 и 27017 свободны
lsof -i :8000
lsof -i :8081
lsof -i :5432
lsof -i :27017

# Остановите конфликтующие процессы или измените порты в docker-compose.yml
```

### Проблемы с Docker
```bash
# Пересоберите образы без кэша
docker-compose build --no-cache

# Очистите Docker систему
docker system prune -f
```

### Проблемы с PostgreSQL
```bash
# Проверьте логи PostgreSQL
docker-compose logs postgres

# Пересоздайте базу данных
make db-reset

# Проверьте строку подключения в .env
echo $DATABASE_URL
```

### Проблемы с MongoDB
```bash
# Проверьте логи MongoDB
docker-compose logs mongodb

# Проверьте подключение
docker-compose exec mongodb mongo --eval "db.adminCommand('ismaster')"

# Проверьте строку подключения MongoDB в .env
echo $MONGODB_URL
```

### Проблемы с токенами
```bash
# Проверьте SECRET_KEY в .env
# Убедитесь, что токен не истек (default: 30 минут)
# Проверьте формат: "Bearer YOUR_TOKEN"
```

## Контакты

**Студент**: Гудынин Данила Денисович  
**Группа**: М8О-109СВ-24  
**Вариант**: 12 (Бюджетирование)

## Требования к лабораторной работе №4

1. ✅ Для сервиса управления данными создано долговременное хранилище данных в noSQL базе данных MongoDB 4.0
2. ✅ Выбран сервис транзакций (не связанный с клиентскими данными) для хранения в MongoDB, клиентские данные остаются в PostgreSQL
3. ✅ Создан скрипт по наполнению MongoDB тестовыми значениями, который запускается при первом запуске сервиса
4. ✅ Для сущности транзакций созданы запросы к MongoDB (CRUD) согласно ранее разработанной архитектуре
5. ✅ Созданы индексы, ускоряющие запросы в MongoDB
6. ✅ Применено индексирование по полям поиска (plan_id, user_id, type, category, created_at, amount)
7. ⏳ Актуализирована модель архитектуры в Structurizr DSL
8. ✅ Сервисы запускаются через docker-compose командой docker-compose up

## Технологии (согласно рекомендациям)

### Используемые технологии для Python:
- **FastAPI** для построения интерфейсов ✅
- **Pydantic** для валидации моделей ✅
- **PyMongo** для работы с СУБД MongoDB ✅
- **SQLAlchemy** для работы с PostgreSQL ✅
- **bcrypt** для хеширования паролей ✅
- **MongoDB 4.0** как noSQL СУБД ✅
- **PostgreSQL 14** как реляционная СУБД ✅
- **Docker & Docker Compose** для контейнеризации ✅

### Пример структуры MongoDB модели:
```python
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional

class TransactionType(str, Enum):
    income = "income"
    expense = "expense"

class TransactionMongo(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    plan_id: int
    type: TransactionType
    amount: float
    description: str
    category: str
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def to_mongo(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if "_id" in data and data["_id"] is None:
            del data["_id"]
        return data

    @classmethod
    def from_mongo(cls, data):
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return cls(**data)
```

### Пример индексов MongoDB:
```javascript
// Создание индексов для оптимизации запросов
db.transactions.createIndex({ "plan_id": 1 });
db.transactions.createIndex({ "user_id": 1 });
db.transactions.createIndex({ "type": 1 });
db.transactions.createIndex({ "category": 1 });
db.transactions.createIndex({ "created_at": 1 });
db.transactions.createIndex({ "amount": 1 });
db.transactions.createIndex({ "plan_id": 1, "user_id": 1 });
```

## Статистика тестирования

### Результаты pytest:
- ✅ **66 тестов прошли успешно**
- ⏩ **9 MongoDB тестов пропускаются** при отсутствии подключения в изолированной среде
- 📊 **Успешность: 88%** (66 из 75 тестов)

### Функциональное тестирование:
- ✅ **PostgreSQL**: Пользователи и планы бюджета
- ✅ **MongoDB**: Транзакции с полным CRUD
- ✅ **API Gateway**: JWT аутентификация и проксирование
- ✅ **Интеграция**: Взаимодействие между сервисами
- ✅ **Docker Compose**: Запуск всех сервисов

## Вариант 12
Бюджетирование с гибридным хранением:
- **PostgreSQL**: Пользователи, планы бюджета
- **MongoDB**: Транзакции и аналитика
- **API**: REST API для всех операций
