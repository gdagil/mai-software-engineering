// Переключаемся на базу данных транзакций
db = db.getSiblingDB('transactions_db');

// Создаем коллекцию транзакций
db.createCollection('transactions');

// Создаем индексы для оптимизации поиска
db.transactions.createIndex({ "plan_id": 1 });
db.transactions.createIndex({ "user_id": 1 });
db.transactions.createIndex({ "type": 1 });
db.transactions.createIndex({ "category": 1 });
db.transactions.createIndex({ "created_at": -1 });
db.transactions.createIndex({ "amount": 1 });

// Составной индекс для поиска по пользователю и плану
db.transactions.createIndex({ "user_id": 1, "plan_id": 1 });

// Составной индекс для поиска по типу и категории
db.transactions.createIndex({ "type": 1, "category": 1 });

// Составной индекс для аналитики по дате и типу
db.transactions.createIndex({ "created_at": -1, "type": 1 });

print("Collections and indexes created successfully!");

// Вставляем тестовые данные
const testTransactions = [
    {
        plan_id: 1,
        type: "income",
        amount: 5000.0,
        description: "Salary payment",
        category: "salary",
        user_id: "admin",
        created_at: new Date("2024-01-01T10:00:00Z")
    },
    {
        plan_id: 1,
        type: "expense",
        amount: 1200.0,
        description: "Rent payment",
        category: "housing",
        user_id: "admin",
        created_at: new Date("2024-01-02T14:30:00Z")
    },
    {
        plan_id: 1,
        type: "expense",
        amount: 350.0,
        description: "Grocery shopping",
        category: "food",
        user_id: "admin",
        created_at: new Date("2024-01-03T09:15:00Z")
    },
    {
        plan_id: 1,
        type: "expense",
        amount: 80.0,
        description: "Gas station",
        category: "transportation",
        user_id: "admin",
        created_at: new Date("2024-01-04T16:45:00Z")
    },
    {
        plan_id: 2,
        type: "income",
        amount: 2000.0,
        description: "Freelance project",
        category: "freelance",
        user_id: "admin",
        created_at: new Date("2024-01-05T11:20:00Z")
    },
    {
        plan_id: 2,
        type: "expense",
        amount: 150.0,
        description: "Internet bill",
        category: "utilities",
        user_id: "admin",
        created_at: new Date("2024-01-06T13:00:00Z")
    },
    {
        plan_id: 1,
        type: "income",
        amount: 500.0,
        description: "Bonus payment",
        category: "bonus",
        user_id: "admin",
        created_at: new Date("2024-01-07T15:30:00Z")
    },
    {
        plan_id: 2,
        type: "expense",
        amount: 45.0,
        description: "Coffee shop",
        category: "entertainment",
        user_id: "admin",
        created_at: new Date("2024-01-08T08:45:00Z")
    }
];

// Вставляем тестовые транзакции
db.transactions.insertMany(testTransactions);

print(`Inserted ${testTransactions.length} test transactions`);

// Выводим статистику
print("Database initialization completed!");
print("Transactions collection statistics:");
print("Total documents: " + db.transactions.count());
print("Indexes created: " + db.transactions.getIndexes().length); 