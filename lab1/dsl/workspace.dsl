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
                description "API шлюз для маршрутизации запросов"
                technology "Node.js, Express"
            }

            budgetService = container "Budget Service" {
                description "Сервис управления бюджетом и транзакциями"
                technology "Java Spring Boot"
            }

            planningService = container "Planning Service" {
                description "Сервис финансового планирования"
                technology "Java Spring Boot"
            }

            analyticsService = container "Analytics Service" {
                description "Сервис аналитики и отчетов"
                technology "Python FastAPI"
            }

            notificationService = container "Notification Service" {
                description "Сервис уведомлений"
                technology "Node.js"
            }

            // Databases
            userDB = container "User Database" {
                description "База данных пользователей"
                technology "PostgreSQL"
            }

            transactionDB = container "Transaction Database" {
                description "База данных транзакций"
                technology "MongoDB"
            }

            planningDB = container "Planning Database" {
                description "База данных финансовых планов"
                technology "PostgreSQL"
            }

            analyticsDB = container "Analytics Database" {
                description "База данных аналитики"
                technology "ClickHouse"
            }

            // Relationships
            user -> webApp "Использует" "HTTPS"
            user -> mobileApp "Использует" "HTTPS"

            webApp -> apiGateway "Отправляет запросы" "REST/HTTPS"
            mobileApp -> apiGateway "Отправляет запросы" "REST/HTTPS"

            apiGateway -> budgetService "Маршрутизирует запросы" "REST/HTTPS"
            apiGateway -> planningService "Маршрутизирует запросы" "REST/HTTPS"
            apiGateway -> analyticsService "Маршрутизирует запросы" "REST/HTTPS"

            budgetService -> transactionDB "Читает/записывает транзакции" "MongoDB Driver"
            budgetService -> userDB "Читает данные пользователей" "JDBC"
            budgetService -> analyticsService "Отправляет данные для анализа" "Apache Kafka"

            planningService -> planningDB "Управляет планами" "JDBC"
            planningService -> userDB "Читает данные пользователей" "JDBC"

            analyticsService -> analyticsDB "Анализирует данные" "HTTP/TCP"
            analyticsService -> transactionDB "Читает транзакции" "MongoDB Driver"

            notificationService -> userDB "Читает контакты" "JDBC"
            budgetService -> notificationService "Отправляет события" "Apache Kafka"
            planningService -> notificationService "Отправляет события" "Apache Kafka"
            notificationService -> user "Отправляет уведомления" "Push/Email/SMS"
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
        dynamic coinkeeper "CreateBudgetPlan" "Создание бюджетного плана" {
            user -> coinkeeper.webApp "Создает новый бюджетный план"
            coinkeeper.webApp -> coinkeeper.apiGateway "POST /api/v1/plans"
            coinkeeper.apiGateway -> coinkeeper.planningService "Создает план"
            coinkeeper.planningService -> coinkeeper.planningDB "Сохраняет план"
            coinkeeper.planningService -> coinkeeper.notificationService "Отправляет уведомление"
            coinkeeper.notificationService -> user "Отправляет уведомления" "Push/Email/SMS"
            autolayout lr
        }

        dynamic coinkeeper "AddTransaction" "Добавление транзакции" {
            user -> coinkeeper.mobileApp "Добавляет транзакцию"
            coinkeeper.mobileApp -> coinkeeper.apiGateway "POST /api/v1/transactions"
            coinkeeper.apiGateway -> coinkeeper.budgetService "Создает транзакцию"
            coinkeeper.budgetService -> coinkeeper.transactionDB "Сохраняет транзакцию"
            coinkeeper.budgetService -> coinkeeper.analyticsService "Отправляет данные для анализа"
            coinkeeper.analyticsService -> coinkeeper.analyticsDB "Обновляет аналитику"
            autolayout lr
        }

        dynamic coinkeeper "ViewAnalytics" "Просмотр аналитики" {
            user -> coinkeeper.webApp "Запрашивает аналитику"
            coinkeeper.webApp -> coinkeeper.apiGateway "GET /api/v1/analytics"
            coinkeeper.apiGateway -> coinkeeper.analyticsService "Запрашивает отчет"
            coinkeeper.analyticsService -> coinkeeper.analyticsDB "Получает данные"
            autolayout lr
        }

        theme default
    }
}
