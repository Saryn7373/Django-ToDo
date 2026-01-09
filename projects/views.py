from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Project


class Index(LoginRequiredMixin, generic.ListView):
    template_name = 'projects/index.html'
    context_object_name = 'projects'
    login_url = '/accounts/login/'  # или куда у вас логин

    def get_queryset(self):
        return Project.objects.filter(
            user=self.request.user,
            deleted_at__isnull=True
        ).order_by('-created_at')


class ProjectDetail(LoginRequiredMixin, generic.DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    login_url = '/accounts/login/'

    def get_queryset(self):
        # Только проекты текущего пользователя и не удалённые
        return Project.objects.filter(
            user=self.request.user,
            deleted_at__isnull=True
        )


class ProjectCreate(LoginRequiredMixin, generic.CreateView):
    model = Project
    template_name = 'projects/project_form.html'
    fields = ['title', 'description', 'show_completed']
    login_url = '/accounts/login/'

    def form_valid(self, form):
        # Автоматически привязываем текущего пользователя как владельца
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('projects:project-detail', kwargs={'pk': self.object.pk})

class ProjectUpdate(LoginRequiredMixin, generic.UpdateView):
    model = Project
    template_name = 'projects/project_form.html'
    fields = ['title', 'description', 'show_completed']
    login_url = '/accounts/login/'

    def get_queryset(self):
        # Только свои проекты
        return Project.objects.filter(
            user=self.request.user,
            deleted_at__isnull=True
        )

    def get_success_url(self):
        return reverse_lazy('projects:project-detail', kwargs={'pk': self.object.pk})


class ProjectDelete(LoginRequiredMixin, generic.DeleteView):
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects:index')
    login_url = '/accounts/login/'

    def get_queryset(self):
        return Project.objects.filter(
            user=self.request.user,
            deleted_at__isnull=True
        )

    def delete(self, request, *args, **kwargs):
        project = self.get_object()
        project.deleted_at = timezone.now()
        project.save(update_fields=['deleted_at'])
        return super().delete(request, *args, **kwargs)