# Схема базы данных

## Диаграмма связей

```
Category (1) ----< (N) Project
                        |
                        | (1)
                        |
                        v
                      (N) Response
```

## Таблицы

### 1. Category (Категории Kwork)

```sql
CREATE TABLE category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    kwork_id INTEGER UNIQUE NOT NULL,
    parent_id INTEGER REFERENCES category(id) NULL,
    url VARCHAR(500) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Поля:**
- `id` - внутренний ID
- `name` - название категории (например, "Верстка")
- `kwork_id` - ID категории в системе Kwork (например, 79)
- `parent_id` - ссылка на родительскую категорию (для подкатегорий)
- `url` - полный URL категории
- `is_active` - активна ли категория для парсинга
- `created_at` - дата создания записи
- `updated_at` - дата обновления

**Индексы:**
- PRIMARY KEY на `id`
- UNIQUE на `kwork_id`
- INDEX на `parent_id`

---

### 2. Project (Заказы с Kwork)

```sql
CREATE TABLE project (
    id SERIAL PRIMARY KEY,
    kwork_id INTEGER UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2),
    currency VARCHAR(10) DEFAULT 'RUB',
    category_id INTEGER REFERENCES category(id) NOT NULL,
    url VARCHAR(500) NOT NULL,
    author_name VARCHAR(255),
    author_rating DECIMAL(3, 2),
    deadline VARCHAR(100),
    status VARCHAR(50) DEFAULT 'new',
    is_viewed BOOLEAN DEFAULT FALSE,
    parsed_at TIMESTAMP DEFAULT NOW(),
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Поля:**
- `id` - внутренний ID
- `kwork_id` - уникальный ID заказа на Kwork
- `title` - заголовок заказа
- `description` - полное описание заказа
- `price` - цена (бюджет)
- `currency` - валюта (RUB по умолчанию)
- `category_id` - ссылка на категорию
- `url` - прямая ссылка на заказ
- `author_name` - имя заказчика
- `author_rating` - рейтинг заказчика
- `deadline` - срок выполнения (текст)
- `status` - статус: `new`, `viewed`, `responded`, `archived`
- `is_viewed` - просмотрен ли заказ
- `parsed_at` - когда спарсен
- `published_at` - когда опубликован на Kwork
- `created_at` - дата создания записи
- `updated_at` - дата обновления

**Индексы:**
- PRIMARY KEY на `id`
- UNIQUE на `kwork_id`
- INDEX на `category_id`
- INDEX на `status`
- INDEX на `is_viewed`
- INDEX на `parsed_at`

---

### 3. Response (Отклики пользователя)

```sql
CREATE TABLE response (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES project(id) ON DELETE CASCADE NOT NULL,
    sent_at TIMESTAMP DEFAULT NOW(),
    notes TEXT,
    status VARCHAR(50) DEFAULT 'sent',
    result VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Поля:**
- `id` - внутренний ID
- `project_id` - ссылка на заказ
- `sent_at` - когда отправлен отклик
- `notes` - заметки пользователя
- `status` - статус отклика: `sent`, `accepted`, `rejected`, `no_answer`
- `result` - результат (получен заказ / нет)
- `created_at` - дата создания записи
- `updated_at` - дата обновления

**Индексы:**
- PRIMARY KEY на `id`
- INDEX на `project_id`
- INDEX на `sent_at`

---

### 4. ParsingSession (История парсинга) - опционально

```sql
CREATE TABLE parsing_session (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES category(id),
    started_at TIMESTAMP DEFAULT NOW(),
    finished_at TIMESTAMP,
    projects_found INTEGER DEFAULT 0,
    projects_new INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'running',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Поля:**
- `id` - внутренний ID
- `category_id` - какая категория парсилась
- `started_at` - начало парсинга
- `finished_at` - конец парсинга
- `projects_found` - всего найдено заказов
- `projects_new` - новых заказов добавлено
- `status` - статус: `running`, `completed`, `failed`
- `error_message` - сообщение об ошибке
- `created_at` - дата создания

**Индексы:**
- PRIMARY KEY на `id`
- INDEX на `category_id`
- INDEX на `started_at`

---

## Django Models (предварительный код)

```python
# projects/models.py

from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    kwork_id = models.IntegerField(unique=True, verbose_name="ID на Kwork")
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='subcategories',
        verbose_name="Родительская категория"
    )
    url = models.URLField(max_length=500, verbose_name="URL")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        return self.name


class Project(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('viewed', 'Просмотрен'),
        ('responded', 'Отклик отправлен'),
        ('archived', 'Архив'),
    ]

    kwork_id = models.IntegerField(unique=True, verbose_name="ID на Kwork")
    title = models.CharField(max_length=500, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Цена"
    )
    currency = models.CharField(max_length=10, default='RUB', verbose_name="Валюта")
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name="Категория"
    )
    url = models.URLField(max_length=500, verbose_name="URL")
    author_name = models.CharField(max_length=255, blank=True, verbose_name="Заказчик")
    author_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Рейтинг заказчика"
    )
    deadline = models.CharField(max_length=100, blank=True, verbose_name="Срок")
    status = models.CharField(
        max_length=50, 
        choices=STATUS_CHOICES, 
        default='new',
        verbose_name="Статус"
    )
    is_viewed = models.BooleanField(default=False, verbose_name="Просмотрен")
    parsed_at = models.DateTimeField(default=timezone.now, verbose_name="Спарсен")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Опубликован")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-parsed_at']

    def __str__(self):
        return self.title


class Response(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Отправлен'),
        ('accepted', 'Принят'),
        ('rejected', 'Отклонен'),
        ('no_answer', 'Нет ответа'),
    ]

    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name="Заказ"
    )
    sent_at = models.DateTimeField(default=timezone.now, verbose_name="Дата отправки")
    notes = models.TextField(blank=True, verbose_name="Заметки")
    status = models.CharField(
        max_length=50, 
        choices=STATUS_CHOICES, 
        default='sent',
        verbose_name="Статус"
    )
    result = models.CharField(max_length=50, blank=True, verbose_name="Результат")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Отклик"
        verbose_name_plural = "Отклики"
        ordering = ['-sent_at']

    def __str__(self):
        return f"Отклик на {self.project.title}"
```

## Начальные данные (fixtures)

Категории Kwork для загрузки:

```json
[
  {"name": "Разработка и IT", "kwork_id": 11, "parent": null, "url": "https://kwork.ru/projects?c=11"},
  {"name": "Верстка", "kwork_id": 79, "parent": 11, "url": "https://kwork.ru/projects?c=79"},
  {"name": "Десктоп программирование", "kwork_id": 80, "parent": 11, "url": "https://kwork.ru/projects?c=80"},
  {"name": "Доработка и настройка сайта", "kwork_id": 38, "parent": 11, "url": "https://kwork.ru/projects?c=38"},
  {"name": "Игры", "kwork_id": 40, "parent": 11, "url": "https://kwork.ru/projects?c=40"},
  {"name": "Мобильные приложения", "kwork_id": 39, "parent": 11, "url": "https://kwork.ru/projects?c=39"},
  {"name": "Сервера и хостинг", "kwork_id": 255, "parent": 11, "url": "https://kwork.ru/projects?c=255"},
  {"name": "Скрипты, боты и mini apps", "kwork_id": 41, "parent": 11, "url": "https://kwork.ru/projects?c=41"},
  {"name": "Создание сайта", "kwork_id": 37, "parent": 11, "url": "https://kwork.ru/projects?c=37"},
  {"name": "Юзабилити, тесты и помощь", "kwork_id": 81, "parent": 11, "url": "https://kwork.ru/projects?c=81"}
]
```
