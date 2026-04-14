from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.projects.models import Project


class Response(models.Model):
    """Отклик на заказ."""

    STATUS_CHOICES: list[tuple] = [
        ("sent", "Отправлен"),
        ("accepted", "Принят"),
        ("rejected", "Отклонен"),
        ("no_answer", "Нет ответа"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="responses",
        verbose_name="Заказ",
    )
    sent_at = models.DateTimeField(default=timezone.now, verbose_name="Дата отправки")
    notes = models.TextField(blank=True, verbose_name="Заметки")
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default="sent", verbose_name="Статус"
    )
    result = models.CharField(max_length=50, blank=True, verbose_name="Результат")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Отклик"
        verbose_name_plural = "Отклики"
        ordering = ["-sent_at"]

    def __str__(self) -> str:
        return f"Отклик на {self.project.title}"

    def clean(self) -> None:
        """Валидация данных модели."""
        super().clean()
        if self.status in ("accepted", "rejected") and not self.result:
            raise ValidationError(
                {"result": "Поле результат обязательно при статусе принят/отклонен"}
            )
