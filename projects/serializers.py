from rest_framework import serializers
from .models import Project, ProjectMembership


class ProjectMembershipSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = ProjectMembership
        fields = ['user', 'role', 'joined_at']


class ProjectSerializer(serializers.ModelSerializer):
    users = ProjectMembershipSerializer(source='projectmembership_set', many=True, read_only=True)
    task_count = serializers.IntegerField(source='tasks.count', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'show_completed',
            'created_at', 'updated_at',
            'users', 'task_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'users', 'task_count']