workspace {
    name "Coinkeeper"
    description "Система управления личным бюджетом"
    !identifiers hierarchical

    model {
        // Определение пользователей системы
        user = person "Пользователь" {
            description "Пользователь системы управления бюджетом"
        }

        coinkeeper = softwareSystem "Coinkeeper" {
            description "Система для управления личным бюджетом и финансового планирования"

            // Frontend containers
            webApp = container "Web Application" {
                description "Веб-интерфейс для управления бюджетом"
                technology "React, TypeScript"
            }

            mobileApp = container "Mobile Application" {
                description "Мобильное приложение для iOS и Android"
                technology "React Native"
            }

            // Backend containers
            apiGateway = container "API Gateway" {
                description "API шлюз для маршрутизации запросов и JWT аутентификации"
                technology "Python FastAPI"
            }

            planningService = container "Planning Service" {
                description "Сервис финансового планирования с кешированием"
                technology "Python FastAPI"
            }

            // Databases
            userDB = container "User Database" {
                description "База данных пользователей и планов"
                technology "PostgreSQL"
            }

            transactionDB = container "Transaction Database" {
                description "База данных транзакций"
                technology "MongoDB"
            }

            redisCache = container "Redis Cache" {
                description "Кеш для оптимизации производительности"
                technology "Redis"
            }

            // Relationships
            user -> webApp "Использует" "HTTPS"
            user -> mobileApp "Использует" "HTTPS"

            webApp -> apiGateway "Отправляет запросы" "REST/HTTPS"
            mobileApp -> apiGateway "Отправляет запросы" "REST/HTTPS"

            apiGateway -> planningService "Проксирует запросы с JWT валидацией" "REST/HTTPS"

            planningService -> userDB "Управляет пользователями и планами" "PostgreSQL Driver"
            planningService -> transactionDB "Управляет транзакциями" "MongoDB Driver"
            planningService -> redisCache "Кеширует данные" "Redis Driver"
        }
    }

    views {
        systemContext coinkeeper {
            include *
            autolayout lr
        }

        container coinkeeper {
            include *
            autolayout lr
        }

        // Динамические представления для ключевых сценариев
        dynamic coinkeeper "CreateBudgetPlan" "Создание бюджетного плана с кешированием" {
            user -> coinkeeper.webApp "Создает новый бюджетный план"
            coinkeeper.webApp -> coinkeeper.apiGateway "POST /api/plans с JWT токеном"
            coinkeeper.apiGateway -> coinkeeper.planningService "Проксирует запрос с X-User заголовком"
            coinkeeper.planningService -> coinkeeper.userDB "Сохраняет план в PostgreSQL"
            coinkeeper.planningService -> coinkeeper.redisCache "Инвалидирует кеш пользователя"
            coinkeeper.planningService -> coinkeeper.redisCache "Кеширует новый план (Write-Behind)"
            coinkeeper.planningService -> coinkeeper.apiGateway "Возвращает созданный план"
            coinkeeper.apiGateway -> coinkeeper.webApp "Возвращает ответ"
            autolayout lr
        }

        dynamic coinkeeper "AddTransaction" "Добавление транзакции" {
            user -> coinkeeper.mobileApp "Добавляет транзакцию"
            coinkeeper.mobileApp -> coinkeeper.apiGateway "POST /api/transactions-mongo"
            coinkeeper.apiGateway -> coinkeeper.planningService "Маршрутизирует запрос"
            coinkeeper.planningService -> coinkeeper.transactionDB "Сохраняет транзакцию в MongoDB"
            autolayout lr
        }

        dynamic coinkeeper "ViewAnalytics" "Просмотр аналитики с кешированием" {
            user -> coinkeeper.webApp "Запрашивает аналитику"
            coinkeeper.webApp -> coinkeeper.apiGateway "GET /api/transactions-mongo/plan/{id}/analytics"
            coinkeeper.apiGateway -> coinkeeper.planningService "Запрашивает отчет"
            coinkeeper.planningService -> coinkeeper.redisCache "Проверяет кеш (Read-Through)"
            coinkeeper.planningService -> coinkeeper.transactionDB "Получает данные из MongoDB"
            coinkeeper.planningService -> coinkeeper.redisCache "Кеширует результат"
            autolayout lr
        }

        theme default
    }
}
