# Kwork Parser

Django-приложение для получения заказов с Kwork через Selenium. Результаты доступны в веб-интерфейсе с фильтрацией и учётом откликов.

## Возможности

- парсинг заказов по категориям Kwork;
- фильтрация и поиск сохранённых заказов;
- учёт отправленных откликов и их статусов;
- запуск парсинга из веб-интерфейса или management-команды;
- управление данными через Django Admin.

## Стек

- Python 3.10+
- Django 5
- Selenium и Beautiful Soup
- PostgreSQL
- Docker Compose

## Быстрый старт

```bash
docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py load_categories
```

Веб-интерфейс будет доступен по адресу `http://localhost:8000/`.

Запуск парсинга из контейнера:

```bash
docker compose exec web python manage.py parse_kwork --category 11
docker compose exec web python manage.py parse_kwork --all
```

Параметры Django и парсера задаются переменными `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `PARSER_DELAY`, `PARSER_TIMEOUT` и `PARSER_MAX_PAGES`. Значения для локального запуска определены в `docker-compose.yml`.

Парсинг необходимо использовать с учётом условий использования Kwork и применимого законодательства.

## Структура проекта

```text
.
├── apps/
│   ├── parser/       # Selenium-парсер и management-команда
│   ├── projects/     # заказы, категории и представления
│   └── responses/    # учёт откликов
├── kwork_parser/     # настройки и маршрутизация Django
├── templates/        # HTML-шаблоны
├── static/           # CSS и JavaScript
├── docs/             # дополнительная документация
├── Dockerfile
├── docker-compose.yml
└── manage.py
```

## Лицензия

MIT
