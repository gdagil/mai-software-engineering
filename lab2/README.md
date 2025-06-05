## Лабараторная работа №2
|              **Студент** | **Группа**   | **Вариант**  |
|--------------------------|--------------|--------------|
| Гудынин Данила Денисович | М8О-109СВ-24 | 12           |

## Описание проекта

Система бюджетирования, состоящая из двух микросервисов:
- **API Gateway** - управление аутентификацией и маршрутизацией запросов
- **Planning Service** - бизнес-логика планов бюджета и транзакций

### Архитектура

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Client/User   │───▶│   API Gateway    │───▶│ Planning Service │
│                 │    │  (Port: 8000)    │    │  (Port: 8080)    │
│                 │    │                  │    │                  │
│ • Authentication│    │ • JWT Auth       │    │ • Business Logic │
│ • API Requests  │    │ • Request Proxy  │    │ • Data Storage   │
│                 │    │ • Token Validate │    │ • In-Memory DB   │
└─────────────────┘    └──────────────────┘    └──────────────────┘
```

## Требования к системе

### Обязательные требования
- [x] HTTP REST API для двух сервисов
- [x] JWT токен аутентификация (Bearer)
- [x] Отдельный endpoint для получения токена
- [x] GET/POST методы
- [x] Хранение данных в памяти
- [x] Мастер-пользователь (admin/secret)
- [x] OpenAPI спецификация
- [x] Docker Compose запуск

### Технический стек
- **Backend**: Python 3.11, FastAPI
- **Authentication**: JWT Bearer tokens
- **Data Storage**: In-Memory (временно)
- **Containerization**: Docker, Docker Compose
- **Testing**: pytest, curl
- **Documentation**: OpenAPI/Swagger

## Быстрый старт

### 1. Клонирование и настройка

```bash
# Перейдите в директорию проекта
cd lab2

# Скопируйте файл конфигурации
cp env.example .env

# (Опционально) Отредактируйте переменные окружения
nano .env
```

### 2. Запуск через Docker Compose

```bash
# Сборка и запуск всех сервисов
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

### Шаг 2: Конфигурация

```bash
# Скопируйте пример конфигурации
cp env.example .env

# Основные настройки в .env:
# SECRET_KEY - секретный ключ для JWT (измените для продакшена)
# PLANNING_SERVICE_URL - URL планирующего сервиса
# ACCESS_TOKEN_EXPIRE_MINUTES - время жизни токена
```

### Шаг 3: Сборка и запуск

```bash
# Сборка Docker образов
make build

# Запуск всех сервисов
make up

# Просмотр логов
make logs

# Остановка сервисов
make down
```

### Шаг 4: Проверка работоспособности

```bash
# Проверка доступности сервисов
curl -f http://localhost:8000/health || echo "API Gateway недоступен"
curl -f http://localhost:8080/health || echo "Planning Service недоступен"
```

## Тестирование системы

### Автоматическое тестирование

```bash
# Запуск всех тестов
make test

# Только unit тесты
make test-unit

# Только интеграционные тесты
make test-integration

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

# Получение планов бюджета
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
- **Администратор**: `admin` / `secret`

## API Endpoints

### API Gateway (http://localhost:8000)

| Метод | Endpoint | Описание | Аутентификация |
|-------|----------|----------|----------------|
| POST | `/auth/login` | Получение JWT токена | Нет |
| GET | `/auth/me` | Информация о пользователе | JWT |
| GET | `/api/plans` | Список планов бюджета | JWT |
| POST | `/api/plans` | Создание плана | JWT |
| GET | `/api/plans/{id}` | Получение плана по ID | JWT |
| PUT | `/api/plans/{id}` | Обновление плана | JWT |
| GET | `/api/transactions` | Список транзакций | JWT |
| POST | `/api/transactions` | Создание транзакции | JWT |
| GET | `/health` | Проверка здоровья | Нет |

### Planning Service (http://localhost:8080)

| Метод | Endpoint | Описание | Аутентификация |
|-------|----------|----------|----------------|
| GET | `/plans` | Список планов | X-User Header |
| POST | `/plans` | Создание плана | X-User Header |
| GET | `/plans/{id}` | Получение плана | X-User Header |
| PUT | `/plans/{id}` | Обновление плана | X-User Header |
| GET | `/transactions` | Список транзакций | X-User Header |
| POST | `/transactions` | Создание транзакции | X-User Header |
| GET | `/plans/{id}/analytics` | Аналитика по плану | X-User Header |
| GET | `/health` | Проверка здоровья | Нет |

## Структура проекта

```
lab2/
├── README.md                    # Документация проекта
├── docker-compose.yml           # Конфигурация Docker Compose
├── Makefile                     # Команды для управления проектом
├── env.example                  # Пример переменных окружения
├── .env                         # Переменные окружения (создается)
├── pytest.ini                  # Конфигурация pytest
├── src/
│   ├── api-gateway/            # API Gateway сервис
│   │   ├── api_gateway/        # Исходный код
│   │   ├── Dockerfile          # Docker образ
│   │   ├── pyproject.toml      # Python зависимости
│   │   └── README.md           # Документация сервиса
│   └── planning-service/       # Planning Service
│       ├── planning_service/   # Исходный код
│       ├── Dockerfile          # Docker образ
│       ├── pyproject.toml      # Python зависимости
│       └── README.md           # Документация сервиса
└── tests/                      # Тесты
    ├── test_api_gateway.py     # Тесты API Gateway
    ├── test_planning_service.py # Тесты Planning Service
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

# Очистка системы
make clean

# Перезапуск сервисов
make down && make up

# Просмотр логов конкретного сервиса
docker-compose logs -f api-gateway
docker-compose logs -f planning-service
```

## Устранение неполадок

### Порты заняты
```bash
# Проверьте, что порты 8000 и 8080 свободны
lsof -i :8000
lsof -i :8080

# Остановите конфликтующие процессы или измените порты в docker-compose.yml
```

### Проблемы с Docker
```bash
# Пересоберите образы без кэша
docker-compose build --no-cache

# Очистите Docker систему
docker system prune -f
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

1. ✅ Создайте HTTP REST API для сервисов, спроектированных в первом задании (по проектированию). Должно быть реализовано как минимум два сервиса (управления пользователем, и хотя бы один «бизнес» сервис)
2. ✅ Сервис должен поддерживать аутентификацию с использованием JWT-token (Bearer)
3. ✅ Должен быть отдельный endpoint для получения токена по логину/паролю
4. ✅ Сервис должен реализовывать как минимум GET/POST методы
5. ✅ Данные сервиса должны храниться в памяти (базу данных добавим потом)
6. ✅ В целях проверки должен быть заведён мастер-пользователь (имя admin, пароль secret)
7. ✅ Сделайте OpenAPI спецификацию и сохраните ее в корне проекта
8. ⏳ Актуализируйте модель архитектуры в Structurizr DSL
9. ✅ Ваши сервисы должны запускаться через docker-compose коммандой docker-compose up (создайте Docker файлы для каждого сервиса)

## Вариант 12
Бюджетирование 
https://about.coinkeeper.me/
