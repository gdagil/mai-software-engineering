# API Gateway Service

Сервис API Gateway для системы бюджетирования.

## Функции
- JWT аутентификация
- Проксирование запросов к Planning Service
- Валидация токенов доступа

## Запуск

### Локально
```bash
poetry install
poetry run uvicorn src.main:app --reload --port 8000
```

### Docker
```bash
docker build -t api-gateway .
docker run -p 8000:8000 api-gateway
```

## Endpoints

- `POST /auth/login` - аутентификация
- `GET /auth/me` - информация о пользователе
- `GET /api/plans` - получить планы
- `POST /api/plans` - создать план
- `GET /api/transactions` - получить транзакции
- `POST /api/transactions` - создать транзакцию
- `GET /health` - проверка здоровья сервиса

## Конфигурация

- PORT: 8000
- Planning Service URL: http://planning-service:8080
