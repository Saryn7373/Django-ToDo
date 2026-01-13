from django.contrib import admin
from .models import Project
from .models import ProjectMembership
from django.db.models import Q
from django.http import HttpResponse
import csv

# Register your models here.

admin.site.register(ProjectMembership)
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'show_completed')
    list_filter = ('show_completed', 'created_at')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        query = request.GET.get('q')
        if query:
            qs = qs.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        return qs
    
    actions = ['export_as_csv']

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