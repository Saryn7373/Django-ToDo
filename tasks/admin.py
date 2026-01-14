from django.contrib import admin
from .models import Task

# Register your models here.

@admin.register(Task)

class TaskAdmin(admin.ModelAdmin):
    # 1. list_display — какие поля показывать в списке задач
    list_display = (
        'title',                    # название задачи
        'project',                  # проект (ссылка на объект)
        'get_status_display',       # человекочитаемый статус
        'author',                   # автор (если есть)
        'created_at',               # дата создания
        'status',             # свойство — завершена или нет
    )

    # 2. list_filter — фильтры справа
    list_filter = (
        'status',                   # по статусу
        'project',                  # по проекту
        'author',                   # по автору (если используется)
        'created_at',               # по дате создания
        'status',             # по свойству завершённости
    )

    # 3. search_fields — поиск по этим полям (вверху страницы)
    search_fields = (
        'title',                    # по названию
        'description',              # по описанию
        'project__title',           # по названию проекта
        'author__username',         # по имени автора (если есть)
    )

    # 4. fields — какие поля показывать при создании/редактировании
    # (убираем ненужные или системные поля из формы)
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

    # Дополнительно: сортировка по умолчанию (новые сверху)
    ordering = ('-created_at',)

    # Делаем поля created_at и updated_at только для чтения
    readonly_fields = ('created_at', 'updated_at')

    # Красивое отображение статуса цветными бейджами (опционально)
    def get_status_display_colored(self, obj):
        colors = {
            'not_started': 'secondary',
            'in_progress': 'primary',
            'under_review': 'warning',
            'done': 'success',
        }
        return f'<span class="badge bg-{colors.get(obj.status, "secondary")}">{obj.get_status_display()}</span>'
    
    get_status_display_colored.short_description = 'Статус'
    get_status_display_colored.allow_tags = True
    
    actions = ['mark_as_done']
    def mark_as_done(self, request, queryset):
        queryset.update(status='done')
    mark_as_done.short_description = "Отметить как выполненные"