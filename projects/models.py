import uuid
from django.db import models
from simple_history.models import HistoricalRecords
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

class ProjectMembership(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=[
            ('owner', 'Владелец'),
            ('member', 'Участник'),
        ],
        default='member',
        verbose_name='Роль'
    )
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата присоединения')
    
    
    class Meta:
        verbose_name = 'Участие в проекте'
        verbose_name_plural = 'Участие в проектах'
        unique_together = ('project', 'user')
    
    def __str__(self):
        return f"{self.user} в {self.project} ({self.role})"

class Project(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectMembership',
        related_name='projects',
        verbose_name='Участники проекта'
    )
    title = models.CharField(max_length=200, verbose_name='title')
    description = models.TextField(blank=True, null=True, verbose_name='description')
    # Настройки проекта
    show_completed = models.BooleanField(
        default=True,
        verbose_name='show completed tasks'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='updated at')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='deleted at')
    history = HistoricalRecords()   
    
    
    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        indexes = [
            # models.Index(fields=['user', 'created_at']),
            # models.Index(fields=['user', 'deleted_at']),
            models.Index(fields=['created_at']),
            models.Index(fields=['deleted_at'])
        ]
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['user', 'title'],
        #         name='unique_project_title_per_user'
        #     )
        # ]
    
    def __str__(self):
        return f"{self.title}"
    
    @property
    def total_tasks(self):
        return self.tasks.count()
    
    @property
    def completed_tasks(self):
        return self.tasks.filter(status='done').count()
    
    @property
    def completion_percentage(self):
        total = self.total_tasks
        if total == 0:
            return 0
        return round((self.completed_tasks / total) * 100, 1)
    
    def save(self, *args, **kwargs):
        if not self.pk and not self.user:
            from django.contrib.auth import get_user_model
            current_user = get_user_model().objects.first()
            if current_user:
                self.user = current_user
        super().save(*args, **kwargs)


class ProjectInvitation(models.Model):
    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE,
        related_name='invitations',
        verbose_name='Проект'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_invitations',
        verbose_name='Создал приглашение'
    )
    token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name='Токен приглашения'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )
    expires_at = models.DateTimeField(
        verbose_name='Истекает',
        null=True,
        blank=True
    )
    is_single_use = models.BooleanField(
        default=True,
        verbose_name='Одноразовая ссылка'
    )
    used_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='used_invitations',
        verbose_name='Использовал'
    )
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата использования'
    )

    class Meta:
        verbose_name = 'Приглашение в проект'
        verbose_name_plural = 'Приглашения в проекты'

    def __str__(self):
        return f"Приглашение в {self.project} от {self.created_by}"

    @property
    def is_expired(self):
        return self.expires_at and self.expires_at < timezone.now()

    @property
    def is_used(self):
        return self.used_by is not None

    @property
    def is_valid(self):
        return not self.is_expired and not (self.is_single_use and self.is_used)

    def get_absolute_url(self):
        return f"/invite/{self.token}/"