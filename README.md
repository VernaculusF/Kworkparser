# Kwork Parser

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-5.0-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Автоматический парсер заказов с биржи фриланса Kwork.ru. Мониторинг новых заказов, фильтрация, отслеживание откликов — всё через удобный веб-интерфейс.

## Возможности

- **Автоматический парсинг** — загрузка заказов с Kwork.ru через Selenium
- **Фильтрация и поиск** — по категории, статусу, ключевым словам
- **Отслеживание откликов** — отметка отправленных откликов и их статусов
- **Real-time обновления** — парсинг в фоне с live-обновлением страницы
- **Админ-панель** — полноценное управление данными через Django Admin
- **Адаптивный дизайн** — Bootstrap 5, работает на мобильных

## Скриншоты

### Главная страница — Список заказов
![Главная страница](docs/screenshots/project_list.png)

### Детальная страница заказа
![Детали заказа](docs/screenshots/project_detail.png)

### Админ-панель
![Админ-панель](docs/screenshots/admin.png)

## Быстрый старт

### Docker (рекомендуемый способ)

```bash
docker-compose up -d
```

Откройте http://localhost:8000/

### Ручная установка

```bash
# 1. Клонировать репозиторий
git clone https://github.com/YOUR_USERNAME/kwork-parser.git
cd kwork-parser

# 2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Настроить окружение
cp .env.example .env
# Отредактируйте .env при необходимости

# 5. Применить миграции
python manage.py migrate

# 6. Создать суперпользователя
python manage.py createsuperuser

# 7. Запустить сервер
python manage.py runserver
```

Откройте http://localhost:8000/

## Использование

### Парсинг через веб-интерфейс

1. Откройте http://localhost:8000/
2. Выберите категорию из выпадающего списка
3. Нажмите "Запустить парсинг"
4. Наблюдайте за появлением заказов в реальном времени

### Парсинг через командную строку

```bash
# Конкретная категория
python manage.py parse_kwork --category 11

# Все активные категории
python manage.py parse_kwork --all

# С ограничением страниц
python manage.py parse_kwork --category 79 --pages 3
```

### Доступные категории

| ID  | Категория                     |
|-----|-------------------------------|
| 11  | Разработка и IT               |
| 79  | Верстка                       |
| 80  | Десктоп программирование       |
| 38  | Доработка и настройка сайта    |
| 40  | Игры                          |
| 39  | Мобильные приложения           |
| 255 | Сервера и хостинг              |
| 41  | Скрипты, боты и mini apps     |
| 37  | Создание сайта                 |
| 81  | Юзабилити, тесты и помощь      |

## Структура проекта

```
kwork-parser/
├── apps/
│   ├── parser/              # Парсер Kwork (Selenium + BS4)
│   │   ├── kwork_parser.py      # Основная логика парсинга
│   │   └── management/commands/ # CLI команды
│   ├── projects/            # Модели заказов и категорий
│   │   ├── models.py            # Category, Project
│   │   ├── views.py             # Views с фильтрацией
│   │   └── admin.py             # Админ-панель
│   └── responses/           # Отклики пользователей
│       ├── models.py            # Response
│       └── views.py             # Views откликов
├── templates/               # HTML шаблоны
├── static/                  # CSS, JS
│   ├── css/main.css
│   └── js/projects.js
├── docs/                    # Документация
├── kwork_parser/            # Настройки Django
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Настройки

Все настройки через переменные окружения (файл `.env`):

| Переменная       | Описание                         | По умолчанию          |
|------------------|---------------------------------|-----------------------|
| `SECRET_KEY`     | Секретный ключ Django            | (генерируется)        |
| `DEBUG`          | Режим отладки                    | `True`                |
| `ALLOWED_HOSTS`  | Разрешённые хосты                | `localhost,127.0.0.1` |
| `PARSER_DELAY`   | Задержка между запросами (сек)   | `2`                   |
| `PARSER_TIMEOUT` | Таймаут загрузки страницы (сек)  | `10`                  |
| `PARSER_MAX_PAGES` | Макс. страниц за один запуск   | `5`                   |

## Разработка

### Pre-commit хуки

```bash
pip install pre-commit
pre-commit install
```

### Запуск тестов

```bash
python manage.py test
```

### Code style

Проект использует Black для форматирования:

```bash
black .
```

## Roadmap

- [ ] Celery + Redis для фоновых задач
- [ ] Уведомления (Telegram/Email)
- [ ] Расширенные фильтры (цена, дата)
- [ ] Экспорт данных (CSV, Excel)
- [ ] REST API (Django REST Framework)
- [ ] Поддержка других бирж (FL.ru, Weblancer)

## Предупреждения

> ⚠️ Парсинг может нарушать условия использования Kwork.ru. Используйте только для личных/образовательных целей.

## Лицензия

[MIT](LICENSE)

## Contributing

См. [CONTRIBUTING.md](CONTRIBUTING.md)

## Changelog

См. [CHANGELOG.md](CHANGELOG.md)
