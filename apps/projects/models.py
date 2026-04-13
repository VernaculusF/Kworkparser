from django.db import models
from django.utils import timezone


class Category(models.Model):
    """Категория заказов на Kwork"""
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
    """Заказ с Kwork"""
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
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['is_viewed']),
            models.Index(fields=['-parsed_at']),
        ]

    def __str__(self):
        return self.title
