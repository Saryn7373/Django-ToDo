from django.contrib import admin
from .models import Project
from .models import ProjectMembership
admin.site.register(ProjectMembership)

# Register your models here.

from django.http import HttpResponse
import csv

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'show_completed')  # добавьте полезные поля
    list_filter = ('show_completed', 'created_at')            # фильтры — удобно
    search_fields = ('title', 'description')                  # поиск
    
    actions = ['export_as_csv']  # ← это ключевая строка, без неё действий не будет!

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(
            content_type='text/csv; charset=utf-8-sig'
        )
        response['Content-Disposition'] = 'attachment; filename=projects_export.csv'
        
        writer = csv.writer(response, delimiter=';')
        
        # Заголовки
        writer.writerow(field_names)
        
        # Данные
        for obj in queryset:
            row = []
            for field in field_names:
                value = getattr(obj, field)
                # Если поле — это datetime, преобразуем в читаемый формат
                if hasattr(value, 'strftime'):
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                row.append(value)
            writer.writerow(row)
            
        return response
    
    export_as_csv.short_description = "Экспорт выбранных проектов в CSV"