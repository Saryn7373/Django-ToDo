from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, get_user_model
from .forms import RegisterForm

from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from projects.models import Project, ProjectMembership
from django.db import transaction


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('projects:index')
    else:
        form = RegisterForm()
    
    return render(request, 'registration/register.html', {'form': form})


User = get_user_model()

class UserDeleteView(UserPassesTestMixin, DeleteView):
    model = User
    success_url = reverse_lazy('admin:auth_user_changelist')

    def test_func(self):
        return self.request.user.is_superuser

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.kwargs['pk'])

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        user = self.get_object()

        owned_projects = Project.objects.filter(
            projectmembership__user=user,
            projectmembership__role='owner'
        )

        if owned_projects.exists():
            for project in owned_projects:
                project.delete()

        return super().delete(request, *args, **kwargs)