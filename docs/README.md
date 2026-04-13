# Документация проекта Kwork Parser

## Содержание

1. **[Обзор проекта](project_overview.md)**
   - Описание и цели
   - Ключевые возможности
   - Технологический стек
   - Архитектура

2. **[План разработки](development_plan.md)**
   - Этапы разработки (8 этапов)
   - Оценка времени
   - Приоритеты для MVP
   - Риски и сложности

3. **[Схема базы данных](database_schema.md)**
   - Диаграмма связей
   - Описание таблиц
   - Django модели
   - Начальные данные (fixtures)

4. **[Технические требования](technical_requirements.md)**
   - Системные требования
   - Зависимости
   - Структура проекта
   - Настройки и конфигурация
   - Безопасность
   - Тестирование

5. **[Анализ парсинга](parser_analysis.md)**
   - Структура URL Kwork
   - Что нужно парсить
   - Технические особенности
   - Стратегия обработки ошибок
   - Оптимизация

## Быстрый старт

### Предварительные требования
- Python 3.11+
- PostgreSQL 14+
- Git

### Установка (после создания проекта)
```bash
# Клонировать репозиторий
git clone https://github.com/your-username/kwork-parser.git
cd kwork-parser

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Установить зависимости
pip install -r requirements.txt

# Настроить .env
cp .env.example .env
# Отредактировать .env с вашими настройками

# Создать БД
createdb kwork_parser

# Применить миграции
python manage.py migrate

# Загрузить начальные данные
python manage.py loaddata categories

# Создать суперпользователя
python manage.py createsuperuser

# Запустить сервер
python manage.py runserver
```

### Использование
```bash
# Запустить парсинг категории
python manage.py parse_kwork --category 11

# Открыть админку
http://localhost:8000/admin

# Открыть главную страницу
http://localhost:8000
```

## Текущий статус

**Этап:** Планирование и проектирование ✅

**Следующие шаги:**
1. Инициализация Django проекта
2. Настройка PostgreSQL
3. Создание моделей данных
4. Исследование структуры Kwork.ru
5. Разработка парсера

## Контакты и поддержка

- GitHub Issues: [создать issue](https://github.com/your-username/kwork-parser/issues)
- Документация: `/docs`

## Лицензия

MIT License (планируется)
