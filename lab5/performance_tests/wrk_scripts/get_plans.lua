-- Lua скрипт для wrk для тестирования GET /api/plans endpoint через API Gateway

-- Загружаем токен из переменной окружения или используем дефолтный
local token = os.getenv("AUTH_TOKEN") or "your_jwt_token_here"

-- Настройка заголовков
wrk.headers["Authorization"] = "Bearer " .. token
wrk.headers["Content-Type"] = "application/json"

-- Функция инициализации
function init(args)
    print("Starting performance test for GET /api/plans (with caching)")
    print("Token: " .. string.sub(token, 1, 20) .. "...")
end

-- Функция для каждого запроса
function request()
    return wrk.format("GET", "/api/plans")
end

-- Функция обработки ответа
function response(status, headers, body)
    if status ~= 200 then
        print("Error: " .. status .. " - " .. body)
    end
end

-- Функция завершения тестирования
function done(summary, latency, requests)
    io.write("-------- Summary (WITH CACHE) --------\n")
    io.write(string.format("Requests: %d\n", summary.requests))
    io.write(string.format("Duration: %.2fs\n", summary.duration / 1000000))
    io.write(string.format("Req/sec: %.2f\n", summary.requests / (summary.duration / 1000000)))
    io.write(string.format("Errors: %d\n", summary.errors.read + summary.errors.write + summary.errors.status + summary.errors.timeout))
    io.write("--------------------------------------\n")
    
    io.write("-------- Latency (WITH CACHE) --------\n")
    io.write(string.format("Min: %.2fms\n", latency.min / 1000))
    io.write(string.format("Max: %.2fms\n", latency.max / 1000))
    io.write(string.format("Mean: %.2fms\n", latency.mean / 1000))
    io.write(string.format("Stdev: %.2fms\n", latency.stdev / 1000))
    io.write(string.format("50th: %.2fms\n", latency:percentile(50) / 1000))
    io.write(string.format("90th: %.2fms\n", latency:percentile(90) / 1000))
    io.write(string.format("99th: %.2fms\n", latency:percentile(99) / 1000))
    io.write("--------------------------------------\n")
end 