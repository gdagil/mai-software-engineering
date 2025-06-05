.PHONY: help build up down logs clean test test-unit test-integration test-all test-smoke test-api save-openapi db-migrate db-upgrade env-check perf-setup perf-test perf-test-1 perf-test-5 perf-test-10 perf-test-all cache-clear cache-stats

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
	@echo ""
	@echo "🚀 Команды тестирования производительности:"
	@echo "  perf-setup   - Подготовить тестовые данные для performance тестов"
	@echo "  perf-test-1  - Запустить тест производительности с 1 потоком"
	@echo "  perf-test-5  - Запустить тест производительности с 5 потоками"
	@echo "  perf-test-10 - Запустить тест производительности с 10 потоками"
	@echo "  perf-test-all- Запустить все тесты производительности"
	@echo "  perf-direct-cache   - Тест Planning Service с кешем (5 потоков)"
	@echo "  perf-direct-no-cache- Тест Planning Service без кеша (5 потоков)"
	@echo "  perf-direct-compare - Сравнительный тест с кешем и без кеша"
	@echo "  cache-clear  - Очистить Redis кеш"
	@echo "  cache-stats  - Показать статистику Redis кеша"

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
	curl http://localhost:8081/health | jq

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

# Performance Testing Commands
perf-setup:
	@echo "🔧 Подготовка тестовых данных для performance тестов..."
	@echo "Ожидание готовности сервисов..."
	@sleep 10
	@echo "Установка зависимостей для скриптов..."
	pip install requests
	@echo "Создание тестовых данных..."
	cd performance_tests/test_scripts && python setup_test_data.py
	@echo "✅ Тестовые данные созданы!"

perf-test-1:
	@echo "🚀 Запуск performance теста с 1 потоком..."
	@$(MAKE) _check_wrk
	@echo "Очистка кеша перед тестом..."
	@$(MAKE) cache-clear
	@echo "Прогрев кеша через API Gateway..."
	@AUTH_TOKEN=$$($(MAKE) _get_token_value) curl -H "Authorization: Bearer $$AUTH_TOKEN" http://localhost:8000/api/plans > /dev/null 2>&1 || true
	@echo "\n=== ТЕСТ С КЕШЕМ через API Gateway (1 поток) ==="
	@AUTH_TOKEN=$$($(MAKE) _get_token_value) wrk -t1 -c1 -d30s -s performance_tests/wrk_scripts/get_plans.lua http://localhost:8000
	@echo "\n=== ТЕСТ БЕЗ КЕША через Planning Service (1 поток) ==="
	@AUTH_TOKEN=$$($(MAKE) _get_token_value) wrk -t1 -c1 -d30s -s performance_tests/wrk_scripts/get_plans_no_cache.lua http://localhost:8081

perf-test-5:
	@echo "🚀 Запуск performance теста с 5 потоками..."
	@$(MAKE) _check_wrk
	@echo "Очистка кеша перед тестом..."
	@$(MAKE) cache-clear
	@echo "Прогрев кеша через API Gateway..."
	@AUTH_TOKEN=$$($(MAKE) _get_token_value) curl -H "Authorization: Bearer $$AUTH_TOKEN" http://localhost:8000/api/plans > /dev/null 2>&1 || true
	@echo "\n=== ТЕСТ С КЕШЕМ через API Gateway (5 потоков) ==="
	@AUTH_TOKEN=$$($(MAKE) _get_token_value) wrk -t5 -c5 -d30s -s performance_tests/wrk_scripts/get_plans.lua http://localhost:8000
	@echo "\n=== ТЕСТ БЕЗ КЕША через Planning Service (5 потоков) ==="
	@AUTH_TOKEN=$$($(MAKE) _get_token_value) wrk -t5 -c5 -d30s -s performance_tests/wrk_scripts/get_plans_no_cache.lua http://localhost:8081

perf-test-10:
	@echo "🚀 Запуск performance теста с 10 потоками..."
	@$(MAKE) _check_wrk
	@echo "Очистка кеша перед тестом..."
	@$(MAKE) cache-clear
	@echo "Прогрев кеша через API Gateway..."
	@AUTH_TOKEN=$$($(MAKE) _get_token_value) curl -H "Authorization: Bearer $$AUTH_TOKEN" http://localhost:8000/api/plans > /dev/null 2>&1 || true
	@echo "\n=== ТЕСТ С КЕШЕМ через API Gateway (10 потоков) ==="
	@AUTH_TOKEN=$$($(MAKE) _get_token_value) wrk -t10 -c10 -d30s -s performance_tests/wrk_scripts/get_plans.lua http://localhost:8000
	@echo "\n=== ТЕСТ БЕЗ КЕША через Planning Service (10 потоков) ==="
	@AUTH_TOKEN=$$($(MAKE) _get_token_value) wrk -t10 -c10 -d30s -s performance_tests/wrk_scripts/get_plans_no_cache.lua http://localhost:8081

perf-test-all:
	@echo "🎯 Запуск полного набора performance тестов..."
	@echo "Подготовка данных..."
	@$(MAKE) perf-setup
	@echo "\n🔥 НАЧИНАЕМ ТЕСТИРОВАНИЕ..."
	@$(MAKE) perf-test-1
	@echo "\n⏳ Пауза между тестами..."
	@sleep 5
	@$(MAKE) perf-test-5
	@echo "\n⏳ Пауза между тестами..."
	@sleep 5
	@$(MAKE) perf-test-10
	@echo "\n✅ Все performance тесты завершены!"

perf-direct-cache:
	@echo "🚀 Тест Planning Service с кешем (5 потоков)..."
	@$(MAKE) _check_wrk
	@echo "Очистка кеша перед тестом..."
	@$(MAKE) cache-clear
	@echo "Прогрев кеша напрямую к Planning Service..."
	@AUTH_TOKEN=$$($(MAKE) _get_token_value) curl -s -H "Authorization: Bearer $$AUTH_TOKEN" -H "X-User: admin" http://localhost:8081/plans > /dev/null && echo "Кеш прогрет"
	@echo "\n=== ТЕСТ С ПРОГРЕТЫМ КЕШЕМ Planning Service (5 потоков) ==="
	@AUTH_TOKEN=$$($(MAKE) _get_token_value) wrk -t5 -c5 -d30s -s performance_tests/wrk_scripts/get_plans_direct_cache.lua http://localhost:8081

perf-direct-no-cache:
	@echo "🚀 Тест Planning Service без кеша (5 потоков)..."
	@$(MAKE) _check_wrk
	@echo "\n=== ТЕСТ БЕЗ КЕША Planning Service (5 потоков) ==="
	@AUTH_TOKEN=$$($(MAKE) _get_token_value) wrk -t5 -c5 -d30s -s performance_tests/wrk_scripts/get_plans_direct_no_cache.lua http://localhost:8081

perf-direct-compare:
	@echo "🚀 Сравнительный тест с кешем и без кеша..."
	@$(MAKE) _check_wrk
	@echo "Очистка кеша перед тестом..."
	@$(MAKE) cache-clear
	@echo "Прогрев кеша напрямую к Planning Service..."
	@AUTH_TOKEN=$$($(MAKE) _get_token_value) curl -s -H "Authorization: Bearer $$AUTH_TOKEN" -H "X-User: admin" http://localhost:8081/plans > /dev/null && echo "Кеш прогрет"
	@echo "\n=== ТЕСТ С ПРОГРЕТЫМ КЕШЕМ Planning Service (5 потоков) ==="
	@AUTH_TOKEN=$$($(MAKE) _get_token_value) wrk -t5 -c5 -d30s -s performance_tests/wrk_scripts/get_plans_direct_cache.lua http://localhost:8081
	@echo "\n⏳ Пауза между тестами..."
	@sleep 5
	@echo "\n=== ТЕСТ БЕЗ КЕША Planning Service (5 потоков) ==="
	@AUTH_TOKEN=$$($(MAKE) _get_token_value) wrk -t5 -c5 -d30s -s performance_tests/wrk_scripts/get_plans_direct_no_cache.lua http://localhost:8081
	@echo "\n✅ Сравнительный тест завершен!"

cache-clear:
	@echo "🗑️ Очистка Redis кеша..."
	@AUTH_TOKEN=$$($(MAKE) _get_token_value) curl -X POST -H "Authorization: Bearer $$AUTH_TOKEN" -H "X-User: admin" http://localhost:8081/cache/clear

cache-stats:
	@echo "📊 Статистика Redis кеша..."
	@AUTH_TOKEN=$$($(MAKE) _get_token_value) curl -H "Authorization: Bearer $$AUTH_TOKEN" -H "X-User: admin" http://localhost:8081/cache/stats | jq

# Helper commands
_check_wrk:
	@which wrk > /dev/null || (echo "❌ wrk не установлен. Установите его: https://github.com/wg/wrk"; exit 1)

_get_token:
	@echo "🔑 Получение JWT токена..."

_get_token_value:
	@curl -s -X POST "http://localhost:8000/auth/login" \
		-H "Content-Type: application/json" \
		-d '{"username": "admin", "password": "secret"}' | jq -r '.access_token'

all: help 