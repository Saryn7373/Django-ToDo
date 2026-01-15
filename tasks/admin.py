from django.contrib import admin
from .models import Task

# Register your models here.

@admin.register(Task)

class TaskAdmin(admin.ModelAdmin):
    # 1. list_display — какие поля показывать в списке задач
    list_display = (
        'title',
        'project',
        'get_status_display',
        'author',
        'created_at',
        'status',
    )

    # 2. list_filter — фильтры справа
    list_filter = (
        'status',
        'project',
        'author',
        'created_at', 
        'status'
    )

    # 3. search_fields — поиск по этим полям (вверху страницы)
    search_fields = (
        'title',
        'description',
        'project__title',
        'author__username',
    )

    # 4. fields — какие поля показывать при создании/редактировании
    fields = (
        'title',
        'description',
        'status',
        'project',
        'author',
        'created_at',
        'updated_at',
    )

    # 5. list_per_page — сколько задач на одной странице списка
    list_per_page = 25

    ordering = ('-created_at',)

    readonly_fields = ('created_at', 'updated_at')