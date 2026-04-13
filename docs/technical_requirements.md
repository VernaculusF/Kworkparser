# Технические требования

## Системные требования

### Разработка
- Python 3.11+
- PostgreSQL 14+
- Git
- pip / poetry для управления зависимостями
- Виртуальное окружение (venv)

### Production
- Linux/Windows Server
- PostgreSQL 14+
- Nginx (reverse proxy)
- Gunicorn / uWSGI
- 1GB RAM минимум
- 10GB HDD

## Зависимости Python

### Core
```
Django==5.0.*
psycopg2-binary==2.9.*
python-decouple==3.8  # для .env
```

### Парсинг
```
requests==2.31.*
beautifulsoup4==4.12.*
lxml==4.9.*
fake-useragent==1.4.*  # ротация User-Agent
```

### Опционально (будущие версии)
```
celery==5.3.*  # фоновые задачи
redis==5.0.*  # брокер для Celery
django-celery-beat==2.5.*  # расписание задач
```

### Development
```
django-debug-toolbar==4.2.*
pytest==7.4.*
pytest-django==4.5.*
black==23.12.*  # форматирование кода
flake8==6.1.*  # линтер
```

## Структура проекта

```
DjangoPython/
├── docs/                          # Документация
│   ├── project_overview.md
│   ├── development_plan.md
│   ├── database_schema.md
│   └── technical_requirements.md
├── kwork_parser/                  # Главный проект Django
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── core/                      # Базовые утилиты
│   │   ├── management/
│   │   ├── templatetags/
│   │   └── utils.py
│   ├── parser/                    # Логика парсинга
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── parse_kwork.py
│   │   ├── parsers/
│   │   │   ├── base.py
│   │   │   └── kwork_parser.py
│   │   └── services.py
│   ├── projects/                  # Модели заказов
│   │   ├── models.py
│   │   ├── admin.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── filters.py
│   ├── responses/                 # Управление откликами
│   │   ├── models.py
│   │   ├── admin.py
│   │   ├── views.py
│   │   └── urls.py
│   └── dashboard/                 # Главная страница
│       ├── views.py
│       ├── urls.py
│       └── templates/
├── static/                        # Статические файлы
│   ├── css/
│   ├── js/
│   └── img/
├── templates/                     # Шаблоны
│   ├── base.html
│   ├── dashboard/
│   ├── projects/
│   └── responses/
├── media/                         # Загружаемые файлы (если нужно)
├── logs/                          # Логи
├── .env.example                   # Пример переменных окружения
├── .gitignore
├── requirements.txt
├── manage.py
├── README.md
└── docker-compose.yml             # Опционально
```

## Переменные окружения (.env)

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=kwork_parser
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Parser settings
PARSER_DELAY=2  # секунды между запросами
PARSER_TIMEOUT=10  # таймаут запроса
PARSER_MAX_PAGES=5  # максимум страниц за раз

# Опционально
# CELERY_BROKER_URL=redis://localhost:6379/0
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-password
```

## Настройки парсера

### Защита от блокировки
1. **User-Agent rotation**
   - Использование fake-useragent
   - Случайная смена User-Agent при каждом запросе

2. **Rate limiting**
   - Задержка между запросами (2-5 секунд)
   - Максимум страниц за один запуск

3. **Обработка ошибок**
   - Retry при 429 (Too Many Requests)
   - Логирование всех ошибок
   - Graceful degradation

### Селекторы для парсинга (примерные)

```python
SELECTORS = {
    'project_list': '.project-item',
    'title': '.project-title',
    'description': '.project-description',
    'price': '.project-price',
    'author': '.project-author',
    'category': '.project-category',
    'date': '.project-date',
    'url': 'a.project-link',
}
```

## API Endpoints (если нужно REST API)

```
GET  /api/projects/              # Список заказов
GET  /api/projects/{id}/         # Детали заказа
POST /api/projects/{id}/view/    # Отметить просмотренным
POST /api/projects/{id}/respond/ # Отметить отклик

GET  /api/categories/            # Список категорий
POST /api/parser/run/            # Запустить парсинг

GET  /api/responses/             # Список откликов
POST /api/responses/             # Создать отклик
```

## Производительность

### Оптимизация БД
- Индексы на часто используемых полях
- `select_related()` и `prefetch_related()` для связанных объектов
- Пагинация (50-100 записей на страницу)

### Кэширование (опционально)
- Redis для кэширования списков
- Cache-Control headers для статики
- Django cache framework

### Парсинг
- Batch insert для новых заказов
- Проверка дубликатов по kwork_id перед парсингом деталей
- Ограничение глубины парсинга

## Безопасность

### Django Security
- `DEBUG=False` в production
- Сильный `SECRET_KEY`
- CSRF protection включен
- XSS protection
- SQL injection protection (ORM)

### Парсинг
- Валидация всех данных перед сохранением
- Санитизация HTML контента
- Ограничение размера данных

### База данных
- Регулярные бэкапы
- Ограничение прав пользователя БД
- SSL соединение (production)

## Логирование

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/kwork_parser.log',
            'formatter': 'verbose',
        },
        'parser_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/parser.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'parser': {
            'handlers': ['parser_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

## Тестирование

### Unit тесты
- Тесты моделей
- Тесты парсера (с mock данными)
- Тесты views
- Покрытие > 70%

### Интеграционные тесты
- Полный цикл парсинга
- Создание откликов
- Фильтрация данных

### Команда запуска
```bash
pytest
pytest --cov=apps  # с покрытием
```

## Docker (опционально)

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: kwork_parser
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
    env_file:
      - .env

volumes:
  postgres_data:
```

## Метрики успеха

### Технические
- Время парсинга < 30 сек для 100 заказов
- Uptime > 99%
- Нет дубликатов в БД
- Покрытие тестами > 70%

### Функциональные
- Корректное определение новых заказов
- Точность парсинга > 95%
- Удобный интерфейс (субъективно)
