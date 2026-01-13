from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Project, ProjectInvitation, ProjectMembership
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from datetime import timedelta
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Q

class OwnerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        project = self.get_object()
        if not project.projectmembership_set.filter(
            user=request.user,
            role='owner'
        ).exists():
            raise PermissionDenied("Только владелец проекта может его редактировать")
        return super().dispatch(request, *args, **kwargs)


class Index(LoginRequiredMixin, generic.ListView):
    template_name = 'projects/index.html'
    context_object_name = 'projects'
    login_url = '/accounts/login/'

    def get_queryset(self):
        return Project.objects.filter(
            users=self.request.user,
            deleted_at__isnull=True
        )


class ProjectDetail(LoginRequiredMixin, generic.DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    login_url = '/accounts/login/'
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        if request.htmx:
            return HttpResponse(render_to_string('projects/comps/tasks_list.html', context, request=request))
        
        return self.render_to_response(context)

    def get_queryset(self):
        return Project.objects.filter(
            users=self.request.user,
            deleted_at__isnull=True
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_owner'] = self.object.projectmembership_set.filter(
            user=self.request.user, 
            role='owner'
        ).exists()
        context['new_invite_url'] = self.request.session.pop('new_invite_url', None)
        
        tasks = self.object.tasks.all()
        if not self.object.show_completed:
            tasks = tasks.filter(~Q(status='done'))

        paginator = Paginator(tasks, 5)
        page = self.request.GET.get('page', 1)

        try:
            tasks_paginated = paginator.page(page)
        except PageNotAnInteger:
            tasks_paginated = paginator.page(1)
        except EmptyPage:
            tasks_paginated = paginator.page(paginator.num_pages)

        context['tasks'] = tasks_paginated
        context['paginator'] = paginator
        return context


class ProjectCreate(LoginRequiredMixin, generic.CreateView):
    model = Project
    template_name = 'projects/project_form.html'
    fields = ['title', 'description', 'show_completed']
    login_url = '/accounts/login/'

    def form_valid(self, form):
        response = super().form_valid(form)
        ProjectMembership.objects.create(
            project=form.instance,
            user=self.request.user,
            role='owner'
        )
        return response

    def get_success_url(self):
        return reverse_lazy('projects:project-detail', kwargs={'pk': self.object.pk})

class ProjectUpdate(LoginRequiredMixin, generic.UpdateView, OwnerRequiredMixin):
    model = Project
    template_name = 'projects/project_form.html'
    fields = ['title', 'description', 'show_completed']
    login_url = '/accounts/login/'

    def get_queryset(self):
        return Project.objects.filter(
            users=self.request.user,
            deleted_at__isnull=True
        )

    def get_success_url(self):
        return reverse_lazy('projects:project-detail', kwargs={'pk': self.object.pk})


class ProjectDelete(LoginRequiredMixin, generic.DeleteView, OwnerRequiredMixin):
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects:index')
    login_url = '/accounts/login/'

    def get_queryset(self):
        return Project.objects.filter(
            users=self.request.user,
            deleted_at__isnull=True
        )

    def delete(self, request, *args, **kwargs):
        project = self.get_object()
        project.deleted_at = timezone.now()
        project.save(update_fields=['deleted_at'])
        return super().delete(request, *args, **kwargs)

class CreateInvitationView(LoginRequiredMixin, generic.View):
    """Создание ссылки-приглашения (только владелец)"""
    
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        
        # Проверяем, что текущий пользователь — владелец
        if not project.projectmembership_set.filter(
            user=request.user, 
            role='owner'
        ).exists():
            messages.error(request, "Только владелец может создавать приглашения")
            return redirect('projects:project-detail', pk=pk)
        
        # Создаём приглашение
        invitation = ProjectInvitation.objects.create(
            project=project,
            created_by=request.user,
            expires_at=timezone.now() + timedelta(days=7),
            is_single_use=True
        )
        
        # Формируем ссылку
        invite_url = request.build_absolute_uri(
            reverse_lazy('projects:accept-invitation', kwargs={'token': invitation.token})
        )
        
        request.session['new_invite_url'] = invite_url
        
        messages.success(
            request,
            f"Ссылка-приглашение создана (действует 7 дней):<br><strong>{invite_url}</strong>"
        )
        
        return redirect('projects:project-detail', pk=pk)


class AcceptInvitationView(generic.View):
    """Принятие приглашения по ссылке"""
    
    def get(self, request, token):
        invitation = get_object_or_404(ProjectInvitation, token=token)
        
        if not invitation.is_valid:
            messages.error(request, "Приглашение недействительно или истекло")
            return redirect('projects:index')
        
        if request.user.is_authenticated:
            # Если пользователь авторизован — сразу добавляем
            if not ProjectMembership.objects.filter(project=invitation.project, user=request.user).exists():
                ProjectMembership.objects.create(
                    project=invitation.project,
                    user=request.user,
                    role='member'
                )
                
                if invitation.is_single_use:
                    invitation.used_by = request.user
                    invitation.used_at = timezone.now()
                    invitation.save()
                
                messages.success(request, f"Вы успешно присоединились к проекту «{invitation.project.title}»!")
            else:
                messages.info(request, "Вы уже участник этого проекта")
        else:
            # Если не авторизован — сохраняем приглашение в сессии и редиректим на логин
            request.session['pending_invite_token'] = str(token)
            messages.info(request, "Войдите или зарегистрируйтесь, чтобы присоединиться к проекту")
            return redirect('/accounts/login')
        
        return redirect('projects:project-detail', pk=invitation.project.pk)


class RemoveMemberView(LoginRequiredMixin, generic.View):
    """Удаление участника из проекта (только владелец)"""

    def post(self, request, pk, user_id):
        project = get_object_or_404(Project, pk=pk)
        
        # Проверяем, что текущий пользователь — владелец
        if not project.projectmembership_set.filter(
            user=request.user,
            role='owner'
        ).exists():
            messages.error(request, "Только владелец проекта может удалять участников")
            return redirect('projects:project-detail', pk=pk)
        
        # Нельзя удалить самого себя (владельца)
        if user_id == request.user.id:
            messages.error(request, "Вы не можете исключить себя из проекта")
            return redirect('projects:project-detail', pk=pk)
        
        # Находим членство
        membership = get_object_or_404(
            ProjectMembership,
            project=project,
            user_id=user_id
        )
        
        # Удаляем участника
        membership.delete()
        
        messages.success(request, f"Пользователь {membership.user.username} исключён из проекта")
        
        return redirect('projects:project-detail', pk=pk)