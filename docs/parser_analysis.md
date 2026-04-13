# Анализ парсинга Kwork.ru

## Структура URL

### Категории
```
Основная категория:
https://kwork.ru/projects?c=11

Подкатегории:
https://kwork.ru/projects?c=79  (Верстка)
https://kwork.ru/projects?c=80  (Десктоп)
https://kwork.ru/projects?c=38  (Доработка сайта)
...
```

### Пагинация (предположительно)
```
https://kwork.ru/projects?c=11&page=1
https://kwork.ru/projects?c=11&page=2
```

### Детальная страница заказа
```
https://kwork.ru/projects/12345678
```

## Что нужно спарсить

### Список заказов (страница категории)

**Обязательные поля:**
- ID заказа (kwork_id)
- Заголовок
- Краткое описание / превью
- Цена (бюджет)
- URL заказа
- Дата публикации

**Опциональные поля:**
- Имя заказчика
- Рейтинг заказчика
- Количество откликов
- Срок выполнения
- Теги / ключевые слова

### Детальная страница заказа

**Дополнительная информация:**
- Полное описание
- Требования
- Файлы (если есть)
- Условия работы
- История заказчика

## Технические особенности

### Возможные препятствия

1. **JavaScript рендеринг**
   - Если контент загружается через JS, нужен Selenium/Playwright
   - Проверка: открыть страницу с отключенным JS

2. **Защита от ботов**
   - Cloudflare / другие WAF
   - Captcha
   - Rate limiting
   - Проверка User-Agent

3. **Динамическая структура**
   - HTML может меняться
   - Нужны гибкие селекторы
   - Fallback стратегии

### Рекомендуемый подход

**Этап 1: Исследование (вручную)**
1. Открыть https://kwork.ru/projects?c=11 в браузере
2. Открыть DevTools (F12)
3. Проверить:
   - Загружается ли контент сразу в HTML
   - Есть ли AJAX запросы
   - Структура DOM элементов
   - Наличие защиты

**Этап 2: Тестовый парсинг**
```python
import requests
from bs4 import BeautifulSoup

url = 'https://kwork.ru/projects?c=11'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
print(response.status_code)
print(response.text[:1000])  # первые 1000 символов

soup = BeautifulSoup(response.text, 'lxml')
# Найти селекторы для заказов
```

**Этап 3: Определение селекторов**
- Найти общий контейнер для списка заказов
- Определить селекторы для каждого поля
- Проверить на нескольких страницах

**Этап 4: Реализация парсера**
```python
class KworkParser:
    BASE_URL = 'https://kwork.ru'
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.get_random_user_agent()
        })
    
    def parse_category(self, category_id, max_pages=5):
        """Парсинг категории"""
        projects = []
        
        for page in range(1, max_pages + 1):
            url = f'{self.BASE_URL}/projects?c={category_id}&page={page}'
            
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                page_projects = self.extract_projects(soup)
                
                if not page_projects:
                    break  # нет больше заказов
                
                projects.extend(page_projects)
                time.sleep(random.uniform(2, 5))  # задержка
                
            except Exception as e:
                logger.error(f'Error parsing page {page}: {e}')
                break
        
        return projects
    
    def extract_projects(self, soup):
        """Извлечение заказов со страницы"""
        projects = []
        
        # TODO: определить правильные селекторы
        items = soup.select('.project-item')  # примерный селектор
        
        for item in items:
            try:
                project = {
                    'kwork_id': self.extract_id(item),
                    'title': item.select_one('.title').text.strip(),
                    'description': item.select_one('.description').text.strip(),
                    'price': self.extract_price(item),
                    'url': self.extract_url(item),
                    'author': item.select_one('.author').text.strip(),
                }
                projects.append(project)
            except Exception as e:
                logger.warning(f'Error extracting project: {e}')
                continue
        
        return projects
    
    def extract_id(self, item):
        """Извлечение ID заказа из URL или data-атрибута"""
        # Реализация зависит от структуры HTML
        pass
    
    def extract_price(self, item):
        """Извлечение и парсинг цены"""
        # Убрать валюту, пробелы, преобразовать в число
        pass
```

## Стратегия обработки ошибок

### HTTP ошибки
```python
def safe_request(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response
            elif response.status_code == 429:
                # Too Many Requests
                wait_time = 2 ** attempt * 5  # exponential backoff
                time.sleep(wait_time)
            elif response.status_code == 403:
                # Forbidden - возможно блокировка
                logger.error('Access forbidden - possible ban')
                return None
            else:
                response.raise_for_status()
                
        except requests.RequestException as e:
            logger.error(f'Request error (attempt {attempt + 1}): {e}')
            if attempt == max_retries - 1:
                return None
            time.sleep(2)
    
    return None
```

### Парсинг ошибки
```python
def safe_extract(item, selector, default=''):
    """Безопасное извлечение данных"""
    try:
        element = item.select_one(selector)
        return element.text.strip() if element else default
    except Exception as e:
        logger.warning(f'Extract error for {selector}: {e}')
        return default
```

## Оптимизация

### Проверка дубликатов перед детальным парсингом
```python
def parse_category_optimized(self, category_id):
    """Парсинг только новых заказов"""
    # 1. Получить список ID со страницы
    project_ids = self.get_project_ids(category_id)
    
    # 2. Проверить, какие уже есть в БД
    existing_ids = Project.objects.filter(
        kwork_id__in=project_ids
    ).values_list('kwork_id', flat=True)
    
    # 3. Парсить только новые
    new_ids = set(project_ids) - set(existing_ids)
    
    for project_id in new_ids:
        project_data = self.parse_project_detail(project_id)
        # Сохранить в БД
```

### Batch insert
```python
def save_projects_batch(projects_data):
    """Массовое сохранение заказов"""
    projects = [
        Project(**data) for data in projects_data
    ]
    Project.objects.bulk_create(projects, ignore_conflicts=True)
```

## Мониторинг и логирование

```python
import logging

logger = logging.getLogger('parser')

class KworkParser:
    def parse_category(self, category_id):
        logger.info(f'Starting parse for category {category_id}')
        start_time = time.time()
        
        try:
            projects = self._do_parse(category_id)
            
            duration = time.time() - start_time
            logger.info(
                f'Parsed {len(projects)} projects in {duration:.2f}s'
            )
            
            return projects
            
        except Exception as e:
            logger.error(f'Parse failed: {e}', exc_info=True)
            raise
```

## Следующие шаги

1. **Исследовать реальную структуру Kwork**
   - Открыть сайт и изучить HTML
   - Определить точные селекторы
   - Проверить наличие защиты

2. **Создать тестовый парсер**
   - Минимальная реализация
   - Парсинг 1 страницы
   - Проверка работоспособности

3. **Итеративная разработка**
   - Добавление полей
   - Обработка edge cases
   - Оптимизация производительности

4. **Интеграция с Django**
   - Management команда
   - Сохранение в БД
   - Логирование
