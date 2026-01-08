from django.db import models
import uuid

class Project(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # user = models.ForeignKey(
    #     User, 
    #     on_delete=models.CASCADE, 
    #     related_name='projects',
    #     verbose_name='Пользователь'
    # )
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
        # indexes = [
        #     models.Index(fields=['user', 'is_archived']),
        #     models.Index(fields=['user', 'is_favorite']),
        # ]
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['user', 'title'],
        #         name='unique_project_title_per_user'
        #     ),
        #     models.UniqueConstraint(
        #         fields=['user'],
        #         condition=models.Q(is_default=True),
        #         name='unique_default_project_per_user'
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
        # if not Project.objects.filter(user=self.user).exists():
        #     self.is_default = True
        super().save(*args, **kwargs)