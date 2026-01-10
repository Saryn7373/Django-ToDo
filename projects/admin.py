from django.contrib import admin
from .models import Project
from .models import ProjectMembership
admin.site.register(Project)
admin.site.register(ProjectMembership)

# Register your models here.