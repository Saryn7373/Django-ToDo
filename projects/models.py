import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Project(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name='project owner',
        null=True,
        blank=True
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
    
    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['user', 'deleted_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'title'],
                name='unique_project_title_per_user'
            )
        ]
    
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
            current_user = get_user_model().objects.first()  # только для тестов/разработки!
            if current_user:
                self.user = current_user
        super().save(*args, **kwargs)