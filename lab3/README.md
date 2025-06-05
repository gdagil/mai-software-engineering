## Лабораторная работа №3
|              **Студент** | **Группа**   | **Вариант**  |
|--------------------------|--------------|--------------|
| Гудынин Данила Денисович | М8О-109СВ-24 | 12           |

## Описание проекта

Система бюджетирования, состоящая из двух микросервисов с постоянным хранилищем данных:
- **API Gateway** - управление аутентификацией и маршрутизацией запросов
- **Planning Service** - бизнес-логика планов бюджета и транзакций с хранением в PostgreSQL

### Архитектура

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Client/User   │───▶│   API Gateway    │───▶│ Planning Service │───▶│   PostgreSQL     │
│                 │    │  (Port: 8000)    │    │  (Port: 8080)    │    │  (Port: 5432)    │
│                 │    │                  │    │                  │    │                  │
│ • Authentication│    │ • JWT Auth       │    │ • Business Logic │    │ • Persistent     │
│ • API Requests  │    │ • Request Proxy  │    │ • CRUD Operations│    │   Data Storage   │
│                 │    │ • Token Validate │    │ • SQLAlchemy ORM │    │ • Indexed Tables │
│                 │    │                  │    │ • Data Validation│    │ • Init Scripts   │
└─────────────────┘    └──────────────────┘    └──────────────────┘    └──────────────────┘
```

## Требования к системе

### Обязательные требования
- [x] HTTP REST API для двух сервисов
- [x] JWT токен аутентификация (Bearer)
- [x] Отдельный endpoint для получения токена
- [x] GET/POST методы
- [x] **Долговременное хранилище данных в PostgreSQL 14**
- [x] **Скрипт создания БД и таблиц с тестовыми данными**
- [x] **CRUD операции для всех сущностей**
- [x] **Хеширование паролей пользователей**
- [x] **Индексирование полей для поиска**
- [x] Мастер-пользователь (admin/secret)
- [x] OpenAPI спецификация
- [x] Docker Compose запуск

### Технический стек
- **Backend**: Python 3.11, FastAPI
- **ORM**: SQLAlchemy (Code First подход)
- **Database**: PostgreSQL 14
- **Validation**: Pydantic
- **Authentication**: JWT Bearer tokens, bcrypt для хеширования
- **Containerization**: Docker, Docker Compose
- **Testing**: pytest, curl
- **Documentation**: OpenAPI/Swagger

## Структура базы данных

### Таблицы
- **users** - пользователи системы (логин, хешированный пароль)
- **budget_plans** - планы бюджета (название, описание, суммы, даты)
- **transactions** - транзакции (тип, сумма, категория, описание)

### Индексы
- `idx_users_username` - по логину пользователя
- `idx_plans_user_id` - по ID пользователя в планах
- `idx_plans_dates` - по датам планов
- `idx_transactions_plan_id` - по ID плана в транзакциях
- `idx_transactions_type` - по типу транзакции
- `idx_transactions_date` - по дате транзакции

## Быстрый старт

### 1. Клонирование и настройка

```bash
# Перейдите в директорию проекта
cd lab3

# Скопируйте файл конфигурации
cp env.example .env

# (Опционально) Отредактируйте переменные окружения
nano .env
```

### 2. Запуск через Docker Compose

```bash
# Сборка и запуск всех сервисов (включая PostgreSQL)
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
curl http://localhost:8080/health

# Проверка подключения к БД
make test-db

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

### Шаг 2: Конфигурация базы данных

```bash
# Скопируйте пример конфигурации
cp env.example .env

# Основные настройки в .env:
# SECRET_KEY - секретный ключ для JWT
# DATABASE_URL - строка подключения к PostgreSQL
# POSTGRES_DB - имя базы данных
# POSTGRES_USER - пользователь БД
# POSTGRES_PASSWORD - пароль БД
# PLANNING_SERVICE_URL - URL планирующего сервиса
# ACCESS_TOKEN_EXPIRE_MINUTES - время жизни токена
```

### Шаг 3: Сборка и запуск

```bash
# Сборка Docker образов
make build

# Запуск всех сервисов (PostgreSQL, API Gateway, Planning Service)
make up

# Просмотр логов
make logs

# Остановка сервисов
make down
```

### Шаг 4: Инициализация базы данных

```bash
# База данных автоматически инициализируется при первом запуске
# Скрипт создает таблицы и вставляет тестовые данные

# Проверка состояния БД
make db-status

# Пересоздание БД (при необходимости)
make db-reset
```

### Шаг 5: Проверка работоспособности

```bash
# Проверка доступности сервисов
curl -f http://localhost:8000/health || echo "API Gateway недоступен"
curl -f http://localhost:8080/health || echo "Planning Service недоступен"

# Проверка подключения к БД
curl -f http://localhost:8080/db/health || echo "База данных недоступна"
```

## Работа с базой данных

### Подключение к PostgreSQL

```bash
# Через Docker Compose
docker-compose exec postgres psql -U budget_user -d budget_db

# Локально (если PostgreSQL установлен)
psql -h localhost -p 5432 -U budget_user -d budget_db
```

### Скрипты инициализации

При первом запуске автоматически выполняются:
- Создание таблиц с индексами
- Вставка тестовых пользователей (включая admin/secret)
- Создание примеров планов бюджета
- Добавление демонстрационных транзакций

### CRUD операции

Все операции реализованы через SQLAlchemy ORM:
- **Create**: Создание новых записей с валидацией
- **Read**: Получение данных с фильтрацией и пагинацией
- **Update**: Обновление существующих записей
- **Delete**: Удаление записей с проверкой зависимостей

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

# Получение планов бюджета из БД
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/plans
```

#### 3. Создание плана бюджета

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

#### 4. Создание транзакции

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

### Интерактивное тестирование

#### Swagger UI
Откройте в браузере:
- API Gateway: http://localhost:8000/docs
- Planning Service: http://localhost:8080/docs

#### Доступные пользователи
- **Администратор**: `admin` / `secret` (пароль хеширован в БД)

## API Endpoints

### API Gateway (http://localhost:8000)

| Метод | Endpoint | Описание | Аутентификация |
|-------|----------|----------|----------------|
| POST | `/auth/login` | Получение JWT токена | Нет |
| POST | `/auth/register` | Регистрация пользователя | Нет |
| GET | `/auth/me` | Информация о пользователе | JWT |
| GET | `/api/plans` | Список планов бюджета | JWT |
| POST | `/api/plans` | Создание плана | JWT |
| GET | `/api/plans/{id}` | Получение плана по ID | JWT |
| PUT | `/api/plans/{id}` | Обновление плана | JWT |
| DELETE | `/api/plans/{id}` | Удаление плана | JWT |
| GET | `/api/transactions` | Список транзакций | JWT |
| POST | `/api/transactions` | Создание транзакции | JWT |
| GET | `/api/transactions/{id}` | Получение транзакции | JWT |
| PUT | `/api/transactions/{id}` | Обновление транзакции | JWT |
| DELETE | `/api/transactions/{id}` | Удаление транзакции | JWT |
| GET | `/health` | Проверка здоровья | Нет |

### Planning Service (http://localhost:8080)

| Метод | Endpoint | Описание | Аутентификация |
|-------|----------|----------|----------------|
| GET | `/plans` | Список планов | X-User Header |
| POST | `/plans` | Создание плана | X-User Header |
| GET | `/plans/{id}` | Получение плана | X-User Header |
| PUT | `/plans/{id}` | Обновление плана | X-User Header |
| DELETE | `/plans/{id}` | Удаление плана | X-User Header |
| GET | `/transactions` | Список транзакций | X-User Header |
| POST | `/transactions` | Создание транзакции | X-User Header |
| GET | `/transactions/{id}` | Получение транзакции | X-User Header |
| PUT | `/transactions/{id}` | Обновление транзакции | X-User Header |
| DELETE | `/transactions/{id}` | Удаление транзакции | X-User Header |
| GET | `/plans/{id}/analytics` | Аналитика по плану | X-User Header |
| GET | `/health` | Проверка здоровья | Нет |
| GET | `/db/health` | Проверка БД | Нет |

## Структура проекта

```
lab3/
├── README.md                    # Документация проекта
├── docker-compose.yml           # Конфигурация Docker Compose (+ PostgreSQL)
├── Makefile                     # Команды для управления проектом
├── env.example                  # Пример переменных окружения
├── .env                         # Переменные окружения (создается)
├── pytest.ini                  # Конфигурация pytest
├── init-db/                     # Скрипты инициализации БД
│   ├── 01-create-tables.sql     # Создание таблиц и индексов
│   └── 02-insert-data.sql       # Вставка тестовых данных
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
│       │   ├── database.py     # Подключение к БД
│       │   ├── models.py       # SQLAlchemy модели
│       │   ├── schemas.py      # Pydantic схемы
│       │   ├── crud.py         # CRUD операции
│       │   └── main.py         # FastAPI приложение
│       ├── Dockerfile          # Docker образ
│       ├── pyproject.toml      # Python зависимости
│       └── README.md           # Документация сервиса
└── tests/                      # Тесты
    ├── test_api_gateway.py     # Тесты API Gateway
    ├── test_planning_service.py # Тесты Planning Service
    ├── test_database.py        # Тесты базы данных
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

# Работа с базой данных
make db-connect      # Подключение к БД
make db-status       # Статус БД
make db-reset        # Пересоздание БД
make db-backup       # Резервная копия
make db-restore      # Восстановление из копии

# Очистка системы
make clean

# Перезапуск сервисов
make down && make up

# Просмотр логов конкретного сервиса
docker-compose logs -f api-gateway
docker-compose logs -f planning-service
docker-compose logs -f postgres
```

## Устранение неполадок

### Порты заняты
```bash
# Проверьте, что порты 8000, 8080 и 5432 свободны
lsof -i :8000
lsof -i :8080
lsof -i :5432

# Остановите конфликтующие процессы или измените порты в docker-compose.yml
```

### Проблемы с Docker
```bash
# Пересоберите образы без кэша
docker-compose build --no-cache

# Очистите Docker систему
docker system prune -f
```

### Проблемы с базой данных
```bash
# Проверьте логи PostgreSQL
docker-compose logs postgres

# Пересоздайте базу данных
make db-reset

# Проверьте строку подключения в .env
echo $DATABASE_URL
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

## Требования к лабораторной работе

1. ✅ Для сервиса управления данными создано долговременное хранилище данных в реляционной СУБД PostgreSQL 14
2. ✅ Создан скрипт по созданию базы данных и таблиц, а также наполнению СУБД тестовыми значениями, который запускается при первом запуске сервиса
3. ✅ Для сущностей созданы запросы к БД (CRUD) согласно ранее разработанной архитектуре
4. ✅ Данные о пользователе включают логин и пароль. Пароль хранится в закрытом виде (хеширован с использованием bcrypt)
5. ✅ Применено индексирование по полям, по которым производится поиск
6. ⏳ Актуализирована модель архитектуры в Structurizr DSL
7. ✅ Сервисы запускаются через docker-compose командой docker-compose up

## Рекомендации по технологиям

### Используемые технологии:
- **FastAPI** для построения интерфейсов
- **Pydantic** для валидации моделей
- **SQLAlchemy** для работы с СУБД (Code First подход)
- **bcrypt** для хеширования паролей
- **PostgreSQL 14** как основная СУБД
- **Docker & Docker Compose** для контейнеризации

### Пример структуры SQLAlchemy модели:
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    
    # Индексы для оптимизации поиска
    __table_args__ = (
        Index('idx_users_username', 'username'),
        Index('idx_users_active', 'is_active'),
    )
```

## Вариант 12
Бюджетирование 
https://about.coinkeeper.me/
