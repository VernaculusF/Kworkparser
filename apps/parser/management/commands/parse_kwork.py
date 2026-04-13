from typing import Any

from django.core.management.base import BaseCommand
from django.conf import settings

from apps.parser.kwork_parser import KworkParser
from apps.projects.models import Category


class Command(BaseCommand):
    """Management команда для парсинга заказов с Kwork.ru."""

    help = 'Парсинг заказов с Kwork.ru'

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--category',
            type=int,
            help='ID категории для парсинга (kwork_id)'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Парсить все активные категории'
        )
        parser.add_argument(
            '--pages',
            type=int,
            default=None,
            help='Максимум страниц для парсинга (по умолчанию из настроек)'
        )

    def handle(self, *args: Any, **options: Any) -> None:
        category_id = options.get('category')
        parse_all = options.get('all')
        max_pages = options.get('pages') or settings.PARSER_MAX_PAGES

        # Инициализация парсера
        parser = KworkParser(
            delay=settings.PARSER_DELAY,
            timeout=settings.PARSER_TIMEOUT,
            max_pages=max_pages
        )

        if parse_all:
            # Парсинг всех активных категорий
            categories = Category.objects.filter(is_active=True)
            
            if not categories.exists():
                self.stdout.write(self.style.WARNING('Нет активных категорий для парсинга'))
                return
            
            self.stdout.write(self.style.SUCCESS(f'Начинаем парсинг {categories.count()} категорий...'))
            
            total_new = 0
            for category in categories:
                self.stdout.write(f'\n--- Парсинг категории: {category.name} ---')
                new_count = parser.parse_category(category.kwork_id, max_pages)
                total_new += new_count
                self.stdout.write(self.style.SUCCESS(f'Найдено новых заказов: {new_count}'))
            
            self.stdout.write(self.style.SUCCESS(f'\n[OK] Парсинг завершен. Всего новых заказов: {total_new}'))
            
        elif category_id:
            # Парсинг конкретной категории
            try:
                category = Category.objects.get(kwork_id=category_id)
                self.stdout.write(f'Парсинг категории: {category.name}')
                
                new_count = parser.parse_category(category_id, max_pages)
                
                self.stdout.write(self.style.SUCCESS(f'[OK] Найдено новых заказов: {new_count}'))
                
            except Category.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Категория с ID {category_id} не найдена')
                )
                self.stdout.write('Доступные категории:')
                for cat in Category.objects.all():
                    self.stdout.write(f'  - {cat.kwork_id}: {cat.name}')
        else:
            self.stdout.write(
                self.style.ERROR('Укажите --category <ID> или --all')
            )
            self.stdout.write('\nПримеры использования:')
            self.stdout.write('  python manage.py parse_kwork --category 11')
            self.stdout.write('  python manage.py parse_kwork --all')
            self.stdout.write('  python manage.py parse_kwork --category 79 --pages 3')
