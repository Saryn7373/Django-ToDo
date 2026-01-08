from django.shortcuts import render
from django.http import HttpResponseRedirect

# Create your views here.

from django.views import generic
from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import get_object_or_404
from projects.models import Project
from .models import Task


class TaskList(generic.ListView):
    """Список всех задач (опционально — можно использовать только внутри проекта)"""
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        # Показываем только не удалённые задачи, можно добавить фильтр по проекту
        return Task.objects.filter(project__deleted_at__isnull=True).order_by('-created_at')


class TaskDetail(generic.DetailView):
    """Детальная страница задачи"""
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

    def get_queryset(self):
        # Только задачи из активных проектов
        return Task.objects.filter(project__deleted_at__isnull=True)


class TaskCreate(generic.CreateView):
    """Создание новой задачи"""
    model = Task
    template_name = 'tasks/task_form.html'
    fields = ['project', 'title', 'description', 'status']
    success_url = reverse_lazy('projects:index')
    
    def get_initial(self):
        initial = super().get_initial()
        project_id = self.request.GET.get('project')
        if project_id:
            project = get_object_or_404(Project, id=project_id, deleted_at__isnull=True)
            initial['project'] = project
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Новая задача'
        return context

    def get_success_url(self):
        return reverse_lazy('projects:project-detail', kwargs={'pk': self.object.project.id})


class TaskUpdate(generic.UpdateView):
    """Редактирование задачи"""
    model = Task
    template_name = 'tasks/task_form.html'
    fields = ['project', 'title', 'description', 'status']

    def get_queryset(self):
        return Task.objects.filter(project__deleted_at__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Редактировать задачу'
        return context

    def get_success_url(self):
        return reverse_lazy('projects:project-detail', kwargs={'pk': self.object.project.id})


class TaskDelete(generic.DeleteView):
    """Мягкое удаление задачи (можно добавить поле deleted_at в Task, если нужно)"""
    model = Task
    template_name = 'tasks/task_confirm_delete.html'

    def get_queryset(self):
        return Task.objects.filter(project__deleted_at__isnull=True)

    def get_success_url(self):
        return reverse_lazy('projects:project-detail', kwargs={'pk': self.object.project.id})

    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        task.deleted_at = timezone.now()
        task.save(update_fields=['deleted_at'])
        return HttpResponseRedirect(self.get_success_url())