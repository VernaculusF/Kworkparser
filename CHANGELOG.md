# Changelog

Все значительные изменения в проекте документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/).

## [Unreleased]

### Добавлено
- Docker и docker-compose для простого развёртывания
- GitHub Actions CI/CD pipeline (lint + checks)
- Pre-commit hooks (black, flake8)
- Type hints для всех Python файлов
- Валидация модели Response
- URLs и views для приложения responses
- CONTRIBUTING.md и CHANGELOG.md

### Изменено
- Вынесены inline JS/CSS из шаблонов в статические файлы
- Устранено дублирование кода в views (project_list/responded_list)
- Magic numbers вынесены в константы
- XSS уязвимость исправлена (innerHTML → DOM API)
- Пустые файлы parser/ удалены
- debug_page.html добавлен в .gitignore
- Обновлён README с badges, скриншотами, структурой

### Исправлено
- `mark_archived` теперь требует POST запрос
- Bare except заменены на конкретные исключения
- `parsed_at` обновляется при редактировании существующего проекта
- debug_page.html сохраняется в BASE_DIR

## [3.1] - 2026-04-13

### Добавлено
- Парсинг полного описания из скрытого блока
- Корректный парсинг цены (убраны HTML комментарии)
- Обновление существующих заказов
- Остановка парсинга после 3 пустых страниц
- Прямые ссылки на Kwork

## [3.0] - 2026-04-13

### Добавлено
- Парсинг всех доступных страниц
- Отображение в реальном времени
- Фоновый парсинг

## [2.0] - 2026-04-13

### Добавлено
- Selenium для обхода JavaScript

## [1.0] - 2026-04-13

### Добавлено
- Первая версия проекта
- Базовый парсинг Kwork
- Модели Category, Project, Response
- Админ-панель
- Веб-интерфейс
