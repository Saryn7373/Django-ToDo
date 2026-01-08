from django.views import generic
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Project


class Index(generic.ListView):
    """Список всех проектов (не удалённых)"""
    template_name = 'projects/index.html'
    context_object_name = 'projects'

    def get_queryset(self):
        # Исключаем мягко удалённые проекты
        return Project.objects.filter(deleted_at__isnull=True).order_by('-created_at')


class ProjectDetail(generic.DetailView):
    """Детальная страница проекта"""
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def get_queryset(self):
        return Project.objects.filter(deleted_at__isnull=True)


class ProjectCreate(generic.CreateView):
    """Создание нового проекта"""
    model = Project
    template_name = 'projects/project_form.html'
    fields = ['title', 'description', 'show_completed']
    success_url = reverse_lazy('projects:index')

    def form_valid(self, form):
        # form.instance.user = self.request.user
        return super().form_valid(form)


class ProjectUpdate(generic.UpdateView):
    """Редактирование проекта"""
    model = Project
    template_name = 'projects/project_form.html'
    fields = ['title', 'description', 'show_completed']
    success_url = reverse_lazy('projects:index')

    def get_queryset(self):
        return Project.objects.filter(deleted_at__isnull=True)


class ProjectDelete(generic.DeleteView):
    """Мягкое удаление проекта"""
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects:index')

    def get_queryset(self):
        return Project.objects.filter(deleted_at__isnull=True)

    def delete(self, request, *args, **kwargs):
        project = self.get_object()
        project.deleted_at = timezone.now()
        project.save(update_fields=['deleted_at'])
        return super().delete(request, *args, **kwargs)