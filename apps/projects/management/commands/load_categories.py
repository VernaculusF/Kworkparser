from typing import Any

from django.core.management.base import BaseCommand

from apps.projects.models import Category

CATEGORIES = [
    # Дизайн
    {"name": "Дизайн", "kwork_id": 15, "parent_id": None},
    {"name": "Арт и иллюстрации", "kwork_id": 28, "parent_id": 15},
    {"name": "Веб и мобильный дизайн", "kwork_id": 24, "parent_id": 15},
    {"name": "ИИ-генерация изображений", "kwork_id": 306, "parent_id": 15},
    {"name": "Интерьер и экстерьер", "kwork_id": 90, "parent_id": 15},
    {"name": "Логотип и брендинг", "kwork_id": 25, "parent_id": 15},
    {"name": "Маркетплейсы и соцсети", "kwork_id": 286, "parent_id": 15},
    {"name": "Наружная реклама", "kwork_id": 272, "parent_id": 15},
    {"name": "Обработка и редактирование", "kwork_id": 68, "parent_id": 15},
    {"name": "Полиграфия", "kwork_id": 27, "parent_id": 15},
    {"name": "Презентации и инфографика", "kwork_id": 270, "parent_id": 15},
    {"name": "Промышленный дизайн", "kwork_id": 250, "parent_id": 15},

    # Разработка и IT
    {"name": "Разработка и IT", "kwork_id": 11, "parent_id": None},
    {"name": "Верстка", "kwork_id": 79, "parent_id": 11},
    {"name": "Десктоп программирование", "kwork_id": 80, "parent_id": 11},
    {"name": "Доработка и настройка сайта", "kwork_id": 38, "parent_id": 11},
    {"name": "Игры", "kwork_id": 40, "parent_id": 11},
    {"name": "Мобильные приложения", "kwork_id": 39, "parent_id": 11},
    {"name": "Сервера и хостинг", "kwork_id": 255, "parent_id": 11},
    {"name": "Скрипты, боты и mini apps", "kwork_id": 41, "parent_id": 11},
    {"name": "Создание сайта", "kwork_id": 37, "parent_id": 11},
    {"name": "Юзабилити, тесты и помощь", "kwork_id": 81, "parent_id": 11},

    # Тексты и переводы
    {"name": "Тексты и переводы", "kwork_id": 5, "parent_id": None},
    {"name": "ИИ-тексты", "kwork_id": 303, "parent_id": 5},
    {"name": "Переводы", "kwork_id": 35, "parent_id": 5},
    {"name": "Продающие и бизнес-тексты", "kwork_id": 74, "parent_id": 5},
    {"name": "Тексты и наполнение сайта", "kwork_id": 73, "parent_id": 5},

    # SEO и трафик
    {"name": "SEO и трафик", "kwork_id": 17, "parent_id": None},
    {"name": "SEO аудиты, консультации", "kwork_id": 44, "parent_id": 17},
    {"name": "Внутренняя оптимизация", "kwork_id": 43, "parent_id": 17},
    {"name": "Продвижение сайта в топ", "kwork_id": 273, "parent_id": 17},
    {"name": "Семантическое ядро", "kwork_id": 71, "parent_id": 17},
    {"name": "Ссылки", "kwork_id": 59, "parent_id": 17},
    {"name": "Статистика и аналитика", "kwork_id": 56, "parent_id": 17},
    {"name": "Трафик", "kwork_id": 72, "parent_id": 17},

    # Соцсети и маркетинг
    {"name": "Соцсети и маркетинг", "kwork_id": 45, "parent_id": None},
    {"name": "E-mail маркетинг и рассылки", "kwork_id": 108, "parent_id": 45},
    {"name": "Базы данных и клиентов", "kwork_id": 113, "parent_id": 45},
    {"name": "Контекстная реклама", "kwork_id": 48, "parent_id": 45},
    {"name": "Маркетинг и PR", "kwork_id": 47, "parent_id": 45},
    {"name": "Маркетплейсы и доски объявлений", "kwork_id": 112, "parent_id": 45},
    {"name": "Соцсети и SMM", "kwork_id": 46, "parent_id": 45},

    # Аудио, видео, съемка
    {"name": "Аудио, видео, съемка", "kwork_id": 7, "parent_id": None},
    {"name": "Аудиозапись и озвучка", "kwork_id": 20, "parent_id": 7},
    {"name": "Видеоролики", "kwork_id": 76, "parent_id": 7},
    {"name": "Видеосъемка и монтаж", "kwork_id": 78, "parent_id": 7},
    {"name": "ИИ-генерация видео", "kwork_id": 300, "parent_id": 7},
    {"name": "Интро и анимация логотипа", "kwork_id": 77, "parent_id": 7},
    {"name": "Музыка и песни", "kwork_id": 23, "parent_id": 7},
    {"name": "Редактирование аудио", "kwork_id": 106, "parent_id": 7},

    # Бизнес и жизнь
    {"name": "Бизнес и жизнь", "kwork_id": 83, "parent_id": None},
    {"name": "Бухгалтерия и налоги", "kwork_id": 64, "parent_id": 83},
    {"name": "Обзвоны и продажи", "kwork_id": 262, "parent_id": 83},
    {"name": "Обучение и консалтинг", "kwork_id": 55, "parent_id": 83},
    {"name": "Персональный помощник", "kwork_id": 84, "parent_id": 83},
    {"name": "Подбор персонала", "kwork_id": 265, "parent_id": 83},
    {"name": "Продажа сайтов и групп", "kwork_id": 114, "parent_id": 83},
    {"name": "Стройка и ремонт", "kwork_id": 65, "parent_id": 83},
    {"name": "Юридическая помощь", "kwork_id": 63, "parent_id": 83},
]


class Command(BaseCommand):
    """Загрузка категорий Kwork с иерархией родитель-потомок."""

    help = 'Загрузить категории Kwork из актуального списка (7 основных + подкатегории)'

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Удалить все существующие категории перед загрузкой',
        )

    def handle(self, *args: Any, **options: Any) -> None:
        if options['reset']:
            count = Category.objects.count()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Удалено {count} существующих категорий'))

        # Сначала создаём основные категории (без parent)
        main_categories = [c for c in CATEGORIES if c['parent_id'] is None]
        sub_categories = [c for c in CATEGORIES if c['parent_id'] is not None]

        for cat_data in main_categories:
            category, created = Category.objects.update_or_create(
                kwork_id=cat_data['kwork_id'],
                defaults={
                    'name': cat_data['name'],
                    'url': f'https://kwork.ru/projects?c={cat_data["kwork_id"]}',
                    'parent': None,
                    'is_active': True,
                },
            )
            status = 'Создана' if created else 'Обновлена'
            self.stdout.write(f'  {status}: {category.name} (ID: {category.kwork_id})')

        # Теперь подкатегории
        for cat_data in sub_categories:
            try:
                parent = Category.objects.get(kwork_id=cat_data['parent_id'])
            except Category.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'  Родительская категория {cat_data["parent_id"]} не найдена для {cat_data["name"]}')
                )
                continue

            category, created = Category.objects.update_or_create(
                kwork_id=cat_data['kwork_id'],
                defaults={
                    'name': cat_data['name'],
                    'url': f'https://kwork.ru/projects?c={cat_data["kwork_id"]}',
                    'parent': parent,
                    'is_active': True,
                },
            )
            status = 'Создана' if created else 'Обновлена'
            self.stdout.write(f'  {status}: {category.name} (ID: {category.kwork_id}) -> {parent.name}')

        total = Category.objects.count()
        main_count = Category.objects.filter(parent__isnull=True).count()
        sub_count = Category.objects.filter(parent__isnull=False).count()
        self.stdout.write(self.style.SUCCESS(
            f'\nЗагружено: {total} категорий ({main_count} основных, {sub_count} подкатегорий)'
        ))
