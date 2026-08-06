# Kwork Parser

A Django application that retrieves Kwork projects with Selenium. Parsed projects are available through a web interface with filtering and response tracking.

## Features

- Parse projects by Kwork category.
- Filter and search stored projects.
- Track submitted responses and their statuses.
- Start parsing from the web interface or a management command.
- Manage data through Django Admin.

## Stack

- Python 3.10+
- Django 5
- Selenium and Beautiful Soup
- PostgreSQL
- Docker Compose

## Quick start

```bash
docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py load_categories
```

The web interface is available at `http://localhost:8000/`.

Run the parser from the container:

```bash
docker compose exec web python manage.py parse_kwork --category 11
docker compose exec web python manage.py parse_kwork --all
```

Django and parser settings use the `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `PARSER_DELAY`, `PARSER_TIMEOUT`, and `PARSER_MAX_PAGES` environment variables. Local defaults are defined in `docker-compose.yml`.

Use the parser in compliance with the Kwork terms of service and applicable law.

## Project structure

```text
.
├── apps/
│   ├── parser/       # Selenium parser and management command
│   ├── projects/     # Projects, categories, and views
│   └── responses/    # Response tracking
├── kwork_parser/     # Django settings and routing
├── templates/        # HTML templates
├── static/           # CSS and JavaScript
├── Dockerfile
├── docker-compose.yml
└── manage.py
```

## License

MIT
