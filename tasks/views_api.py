from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Task.objects.all()
        
        project_id = self.kwargs.get('project_pk')
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
        
        queryset = queryset.filter(project__users=self.request.user)
        
        return queryset