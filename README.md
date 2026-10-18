# find-doc

Асинхронный поисковик по текстам документов на FastAPI + PostgreSQL + Elasticsearch.

## Стек

- Python 3.14
- FastAPI, SQLAlchemy (async), Pydantic
- PostgreSQL 17, Elasticsearch 9.5.5
- uv, just

## Быстрый старт

```bash
just install
docker compose up db elasticsearch -d
just run
```

- Swagger UI: http://localhost:8000/docs

## Импорт данных

```bash
uv run python scripts/seed.py posts.csv
```

## Тесты

```bash
just test
```

## Полная сборка Docker

```bash
just docker-up
```