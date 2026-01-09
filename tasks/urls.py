from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('create/', views.TaskCreate.as_view(), name='task-create'),
    path('<uuid:pk>/', views.TaskDetail.as_view(), name='task-detail'),
    path('<uuid:pk>/update/', views.TaskUpdate.as_view(), name='task-update'),
    path('<uuid:pk>/delete/', views.TaskDelete.as_view(), name='task-delete'),
    path('<uuid:pk>/update-status/', views.TaskUpdateStatus.as_view(), name='task-update-status'),
]