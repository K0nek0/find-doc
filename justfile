# --- Приложение ---
# Запуск сервера в режиме разработки
run:
    uv run uvicorn src.find_doc.main:app --reload --host 127.0.0.1 --port 8000

docker-clean:
    docker compose down -v --rmi all

docker-up:
    docker compose up --build

docker-down:
    docker compose down

health:
    curl -s http://localhost:8000/health

    
# --- Утилиты ---
# Запуск тестов
test:
    uv run pytest --import-mode=importlib -v

# Линтер и форматирование
fmt:
    uv run ruff check --fix src/
    uv run ruff format src/

fmt_tests:
    uv run ruff check --fix tests/
    uv run ruff format tests/
