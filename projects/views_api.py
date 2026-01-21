# projects/views_api.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import Project, ProjectInvitation, ProjectMembership
from .serializers import ProjectSerializer, ProjectInvitationSerializer
from rest_framework import permissions


class IsProjectOwnerOrReadOnly(permissions.BasePermission):
    """Разрешение: только владелец может изменять проект, остальные — только читать"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.projectmembership_set.filter(
            user=request.user,
            role='owner'
        ).exists()


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectOwnerOrReadOnly]

    def get_queryset(self):
        # Только проекты, где текущий пользователь — участник
        return Project.objects.filter(
            users=self.request.user
        ).prefetch_related('projectmembership_set', 'tasks')

    # Фильтры и поиск
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    
    search_fields = ['title', 'description']  # поиск по названию и описанию
    ordering_fields = ['created_at', 'updated_at', 'title']  # сортировка
    ordering = ['-created_at']  # по умолчанию новые сверху

    # Кастомные действия через @action
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def invite(self, request, pk=None):
        """Генерация одноразовой ссылки-приглашения (только владелец)"""
        project = self.get_object()
        
        if not project.projectmembership_set.filter(
            user=request.user, role='owner'
        ).exists():
            return Response(
                {"detail": "Только владелец может приглашать участников"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Создаём приглашение
        invitation = ProjectInvitation.objects.create(
            project=project,
            created_by=request.user,
            expires_at=timezone.now() + timedelta(days=7),
            is_single_use=True
        )

        # Формируем полную ссылку
        invite_url = request.build_absolute_uri(
            reverse('projects:accept-invitation', kwargs={'token': invitation.token})
        )

        return Response({
            "invite_url": invite_url,
            "expires_at": invitation.expires_at,
            "token": str(invitation.token)
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='my-role')
    def my_role(self, request, pk=None):
        """Получение роли текущего пользователя в проекте"""
        project = self.get_object()
        membership = project.projectmembership_set.filter(user=request.user).first()
        
        if membership:
            return Response({
                "role": membership.role,
                "joined_at": membership.joined_at
            })
        else:
            return Response(
                {"detail": "Вы не являетесь участником этого проекта"},
                status=status.HTTP_404_NOT_FOUND
            )