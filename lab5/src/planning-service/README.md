# Planning Service

Бизнес-сервис для управления планами бюджета и транзакциями.

## Функции
- Создание и управление планами бюджета
- Добавление транзакций (доходы/расходы)
- Аналитика по планам
- Хранение данных в памяти

## Запуск

### Локально
```bash
poetry install
poetry run uvicorn src.main:app --reload --port 8080
```

### Docker
```bash
docker build -t planning-service .
docker run -p 8080:8080 planning-service
```

## Endpoints

- `GET /plans` - получить планы пользователя
- `POST /plans` - создать новый план
- `GET /plans/{plan_id}` - получить план по ID
- `PUT /plans/{plan_id}` - обновить план
- `GET /transactions` - получить транзакции
- `POST /transactions` - создать транзакцию
- `GET /plans/{plan_id}/analytics` - аналитика по плану
- `GET /health` - проверка здоровья сервиса

## Модели данных

- **BudgetPlan**: план бюджета с плановыми доходами/расходами
- **Transaction**: транзакция (доход или расход)
- **TransactionType**: тип транзакции (income/expense)

## Конфигурация

- PORT: 8080
- Аутентификация: через заголовок X-User от API Gateway
