from django.db import models

# Create your models here.
from django.db import models
from projects.models import Project 
import uuid


class Task(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', 'Не взята'
        IN_PROGRESS = 'in_progress', 'Выполняется'
        UNDER_REVIEW = 'under_review', 'На проверке'
        DONE = 'done', 'Выполнена'

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Проект'
    )

    title = models.CharField(
        max_length=200,
        verbose_name='Название задачи'
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NOT_STARTED,
        verbose_name='Статус'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    author = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']  # Новые задачи сверху
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_completed(self):
        return self.status == self.Status.DONE

    @property
    def status_display_ru(self):
        return dict(self.Status.choices).get(self.status, self.status)