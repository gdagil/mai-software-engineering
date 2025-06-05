.PHONY: help build up down logs clean test test-unit test-integration test-all test-smoke test-api save-openapi db-migrate db-upgrade env-check

help:
	@echo "Доступные команды:"
	@echo "  build        - Собрать Docker образы"
	@echo "  up           - Запустить все сервисы"
	@echo "  down         - Остановить все сервисы"
	@echo "  logs         - Показать логи сервисов"
	@echo "  clean        - Удалить образы и контейнеры"
	@echo "  test         - Запустить все тесты (pytest)"
	@echo "  test-unit    - Запустить только unit тесты"
	@echo "  test-integration - Запустить только integration тесты"
	@echo "  test-api     - Запустить простые API тесты (curl)"
	@echo "  test-smoke   - Запустить smoke тесты"
	@echo "  save-openapi - Сохранить OpenAPI спецификации"
	@echo "  db-migrate   - Создать новую миграцию"
	@echo "  db-upgrade   - Применить миграции"
	@echo "  env-check    - Проверить настройки окружения"

build:
	docker-compose build

up:
	docker-compose up --build

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v --rmi all
	docker system prune -f

test:
	@echo "🧪 Запуск всех тестов pytest..."
	@echo "Ожидание готовности сервисов..."
	@sleep 5
	@export PYTHONPATH="$(shell pwd)/src/api-gateway:$(shell pwd)/src/planning-service" && \
	python -m pytest tests/ -v --tb=short

test-unit:
	@echo "🔬 Запуск unit тестов..."
	@export PYTHONPATH="$(shell pwd)/src/api-gateway:$(shell pwd)/src/planning-service" && \
	python -m pytest tests/ -v --tb=short -m "not integration"

test-integration:
	@echo "🔗 Запуск integration тестов..."
	@echo "Ожидание готовности сервисов..."
	@sleep 5
	@export PYTHONPATH="$(shell pwd)/src/api-gateway:$(shell pwd)/src/planning-service" && \
	python -m pytest tests/test_integration.py -v --tb=short

test-smoke:
	@echo "💨 Запуск smoke тестов..."
	@export PYTHONPATH="$(shell pwd)/src/api-gateway:$(shell pwd)/src/planning-service" && \
	python -m pytest tests/ -v --tb=short -k "health_check"

test-api:
	@echo "🌐 Тестирование API через curl..."
	@echo "Ожидание запуска сервисов..."
	@sleep 10
	@echo "1. Получение токена:"
	curl -X POST "http://localhost:8000/auth/login" \
		-H "Content-Type: application/json" \
		-d '{"username": "admin", "password": "secret"}' | jq
	@echo "\n2. Проверка здоровья сервисов:"
	curl http://localhost:8000/health | jq
	curl http://localhost:8080/health | jq

save-openapi:
	@echo "Сохранение OpenAPI спецификаций..."
	python save_openapi.py

db-migrate:
	@echo "Создание новой миграции..."
	cd src/planning-service && alembic revision --autogenerate -m "$(MSG)"

db-upgrade:
	@echo "Применение миграций..."
	cd src/planning-service && alembic upgrade head

env-check:
	@echo "Проверка настроек окружения..."
	@echo "1. Проверка файлов конфигурации:"
	@if [ -f .env ]; then \
		echo "Файл .env найден"; \
	else \
		echo "Файл .env не найден. Скопируйте env.example в .env"; \
	fi
	@echo "2. Проверка Docker Compose конфигурации:"
	docker-compose config --quiet && echo "docker-compose.yml корректен" || echo "Ошибка в docker-compose.yml"
	@echo "3. Список переменных окружения:"
	@echo "Основные переменные для настройки:"
	@echo "   - SECRET_KEY (для JWT)"
	@echo "   - DATABASE_URL (для PostgreSQL)" 
	@echo "   - PLANNING_SERVICE_URL (для API Gateway)"
	@echo ""
	@echo "Подробная документация: ENVIRONMENT.md"

all: help 