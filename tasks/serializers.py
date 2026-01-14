from rest_framework import serializers
from .models import Task
from projects.serializers import ProjectSerializer


class TaskSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'project', 'title', 'description', 'status',
            'author', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'author']