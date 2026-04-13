import time
import random
import logging
from decimal import Decimal
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from apps.projects.models import Category, Project

logger = logging.getLogger('parser')


class KworkParser:
    """Парсер заказов с Kwork.ru с использованием Selenium"""
    
    BASE_URL = 'https://kwork.ru'
    
    def __init__(self, delay=2, timeout=10, max_pages=5):
        self.delay = delay
        self.timeout = timeout
        self.max_pages = max_pages
        self.driver = None
        
    def _init_driver(self):
        """Инициализация Selenium WebDriver"""
        if self.driver:
            return
            
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Без GUI
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            # Автоматическая установка ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(self.timeout)
            logger.info('Chrome WebDriver initialized successfully')
        except Exception as e:
            logger.error(f'Failed to initialize Chrome driver: {e}')
            raise
    
    def _close_driver(self):
        """Закрытие WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def parse_category(self, category_id, max_pages=None):
        """
        Парсинг категории
        
        Args:
            category_id: ID категории в Kwork
            max_pages: Максимум страниц для парсинга
            
        Returns:
            Количество новых заказов
        """
        if max_pages is None:
            max_pages = self.max_pages
            
        try:
            category = Category.objects.get(kwork_id=category_id)
        except Category.DoesNotExist:
            logger.error(f'Category with kwork_id={category_id} not found')
            return 0
        
        logger.info(f'Starting parse for category: {category.name} (ID: {category_id})')
        
        # Инициализация драйвера
        self._init_driver()
        
        new_projects_count = 0
        page_new_count = 0
        
        try:
            for page in range(1, max_pages + 1):
                url = f'{self.BASE_URL}/projects?c={category_id}'
                if page > 1:
                    url += f'&page={page}'
                
                logger.info(f'Parsing page {page}: {url}')
                
                try:
                    # Загрузка страницы
                    self.driver.get(url)
                    
                    # Ждем загрузки контента (ждем появления карточек проектов)
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "want-card"))
                        )
                        logger.info('Want-card elements found')
                    except Exception as e:
                        logger.warning(f'Timeout waiting for want-card: {e}')
                    
                    # Дополнительная задержка для полной загрузки JS
                    time.sleep(3)
                    
                    # Получаем HTML после загрузки JS
                    html = self.driver.page_source
                    
                    # Сохраняем HTML для отладки (первая страница)
                    if page == 1:
                        with open('debug_page.html', 'w', encoding='utf-8') as f:
                            f.write(html)
                        logger.info('Saved page HTML to debug_page.html')
                    
                    soup = BeautifulSoup(html, 'lxml')
                    
                    # Проверяем наличие карточек
                    cards = soup.select('.want-card')
                    logger.info(f'Found {len(cards)} want-card elements in HTML')
                    
                    projects = self.extract_projects(soup, category)
                    
                    if not projects:
                        logger.info(f'No projects found on page {page}, stopping')
                        break
                    
                    # Сохранение проектов
                    page_new_count = 0
                    for project_data in projects:
                        created = self.save_project(project_data)
                        if created:
                            new_projects_count += 1
                            page_new_count += 1
                    
                    logger.info(f'Page {page}: found {len(projects)} projects, {page_new_count} new on this page')
                    
                    # Останавливаемся если на странице не было новых проектов
                    if page_new_count == 0:
                        logger.info(f'No new projects on page {page}, stopping parsing')
                        break
                    
                    # Задержка между запросами
                    if page < max_pages:
                        delay = random.uniform(self.delay, self.delay + 2)
                        logger.debug(f'Sleeping {delay:.2f} seconds')
                        time.sleep(delay)
                        
                except Exception as e:
                    logger.error(f'Error parsing page {page}: {e}', exc_info=True)
                    break
        
        finally:
            # Закрываем драйвер
            self._close_driver()
        
        logger.info(f'Parsing completed. Total new projects: {new_projects_count}')
        return new_projects_count
    
    def extract_projects(self, soup, category):
        """
        Извлечение проектов со страницы
        Структура: <div class="want-card want-card--list want-card--hover">
        """
        projects = []
        
        # Реальный селектор из HTML Kwork
        items = soup.select('.want-card')
        
        logger.info(f'Found {len(items)} project items')
        
        for idx, item in enumerate(items):
            try:
                logger.debug(f'Processing item {idx + 1}/{len(items)}')
                project_data = self.extract_project_data(item, category)
                if project_data and project_data.get('kwork_id'):
                    projects.append(project_data)
                    logger.info(f'Successfully extracted project {project_data["kwork_id"]}')
                else:
                    logger.warning(f'Item {idx + 1} returned no data')
            except Exception as e:
                logger.error(f'Error extracting project {idx + 1}: {e}', exc_info=True)
                continue
        
        logger.info(f'Total extracted projects: {len(projects)}')
        return projects
    
    def extract_project_data(self, item, category):
        """
        Извлечение данных одного проекта
        
        Структура HTML Kwork:
        <div class="want-card">
            <h1 class="wants-card__header-title">
                <a href="/projects/3149022">Заголовок</a>
            </h1>
            <div class="wants-card__description-text">
                <div class="overflow-hidden">Краткое...</div>
                <div class="overflow-hidden" style="display: none;">Полное описание</div>
            </div>
            <div class="wants-card__price">500 ₽</div>
        </div>
        """
        
        # Извлечение ID проекта из ссылки
        kwork_id = None
        link = item.select_one('.wants-card__header-title a')
        if link and link.get('href'):
            href = link.get('href')
            if '/projects/' in href:
                try:
                    # Извлекаем ID из URL типа "/projects/3149022"
                    kwork_id = int(href.split('/')[-1])
                except (ValueError, IndexError):
                    pass
        
        if not kwork_id:
            logger.debug(f'Could not extract kwork_id from item')
            return None
        
        # Заголовок
        title = self.safe_extract(item, '.wants-card__header-title a', 'text')
        
        # Описание - парсим полное описание из скрытого блока
        description = ''
        desc_container = item.select_one('.wants-card__description-text')
        if desc_container:
            # Ищем скрытый блок с полным описанием (style="display: none;")
            hidden_block = desc_container.select_one('.breakwords.overflow-hidden[style*="none"]')
            if hidden_block:
                # Берем div внутри скрытого блока
                full_desc = hidden_block.select_one('div.d-inline')
                if full_desc:
                    description = full_desc.get_text(separator=' ', strip=True)
            
            # Если скрытого блока нет, берем видимый
            if not description:
                visible_block = desc_container.select_one('.overflow-hidden .d-inline')
                if visible_block:
                    description = visible_block.get_text(separator=' ', strip=True)
            
            # Убираем лишние пробелы
            description = ' '.join(description.split())
        
        # Цена - парсим из wants-card__price, убираем комментарии
        price_text = ''
        price_elem = item.select_one('.wants-card__price')
        if price_elem:
            # Ищем div с классом d-inline внутри wants-card__price
            price_div = price_elem.select_one('div.d-inline')
            if price_div:
                price_text = price_div.get_text(strip=True)
            else:
                # Если нет d-inline, берем весь текст
                price_text = price_elem.get_text(strip=True)
            
            # Убираем "Цена", "Желаемый бюджет", "до" и т.д.
            price_text = price_text.replace('Цена', '').replace('Желаемый бюджет:', '').replace('до', '').strip()
        
        price = self.parse_price(price_text)
        
        # Автор - ссылка на профиль пользователя
        author = ''
        author_links = item.select('a')
        for a in author_links:
            href = a.get('href', '')
            if '/user/' in href:
                author = a.get_text(strip=True)
                break
        
        # URL проекта
        url = f'{self.BASE_URL}/projects/{kwork_id}'
        
        logger.debug(f'Extracted project: {kwork_id} - {title[:50]} - Price: {price}')
        
        return {
            'kwork_id': kwork_id,
            'title': title or f'Проект #{kwork_id}',
            'description': description or '',
            'price': price,
            'currency': 'RUB',
            'category': category,
            'url': url,
            'author_name': author or '',
            'status': 'new',
            'is_viewed': False,
        }
    
    def safe_extract(self, item, selector, attr='text'):
        """Безопасное извлечение данных"""
        try:
            element = item.select_one(selector)
            if element:
                if attr == 'text':
                    return element.get_text(strip=True)
                else:
                    return element.get(attr, '')
        except Exception:
            pass
        return ''
    
    def parse_price(self, price_text):
        """Парсинг цены из текста"""
        if not price_text:
            return None
        
        try:
            # Убираем все кроме цифр и точки
            price_str = ''.join(c for c in price_text if c.isdigit() or c == '.')
            if price_str:
                return Decimal(price_str)
        except Exception:
            pass
        
        return None
    
    def save_project(self, project_data):
        """
        Сохранение или обновление проекта в БД
        
        Returns:
            True если проект новый, False если уже существует (но обновляется)
        """
        kwork_id = project_data['kwork_id']
        
        # Проверка существования
        existing = Project.objects.filter(kwork_id=kwork_id).first()
        
        if existing:
            # Обновляем существующий проект (цена, описание могли измениться)
            existing.title = project_data['title']
            existing.description = project_data['description']
            existing.price = project_data['price']
            existing.author_name = project_data['author_name']
            existing.url = project_data['url']
            existing.save()
            logger.debug(f'Updated existing project: {kwork_id}')
            return False
        
        try:
            project = Project.objects.create(**project_data)
            logger.info(f'Created new project: {project.title} (ID: {kwork_id})')
            return True
        except Exception as e:
            logger.error(f'Error saving project {kwork_id}: {e}')
            return False
