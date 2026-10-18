FROM python:3.14-slim

# 1. Устанавливаем uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# 2. Системные зависимости для C-расширений (asyncpg и т.д.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# 3. Копируем файлы зависимостей и устанавливаем их
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# 4. Копируем исходный код проекта
COPY . .

# 5. Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH="/app/src"

EXPOSE 8000

# 6. Запуск
CMD ["/app/.venv/bin/uvicorn", "find_doc.main:app", "--host", "0.0.0.0", "--port", "8000"]
