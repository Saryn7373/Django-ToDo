from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('create/', views.ProjectCreate.as_view(), name='project-create'),
    path('<uuid:pk>/', views.ProjectDetail.as_view(), name='project-detail'),
    path('<uuid:pk>/update/', views.ProjectUpdate.as_view(), name='project-update'),
    path('<uuid:pk>/delete/', views.ProjectDelete.as_view(), name='project-delete'),
]