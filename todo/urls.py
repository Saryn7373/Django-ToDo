"""
URL configuration for todo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include
from django.urls import path
from accounts.views import register
from django.views.generic import RedirectView
from accounts.views import UserDeleteView

from rest_framework.routers import DefaultRouter
from projects.views_api import ProjectViewSet
from tasks.views_api import TaskViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'tasks', TaskViewSet)

urlpatterns = [
    path('', RedirectView.as_view(url='/projects/', permanent=True)),
    path('admin/', admin.site.urls),
    path('projects/', include('projects.urls')),
    path('tasks/', include('tasks.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', register, name='register'),
    path('accounts/user/<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('api/', include(router.urls)),
    path('api/projects/<uuid:project_pk>/tasks/', TaskViewSet.as_view({'get': 'list', 'post': 'create'}), name='project-tasks-list')
]