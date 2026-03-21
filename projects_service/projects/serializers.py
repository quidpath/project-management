from rest_framework import serializers
from .models import Project, ProjectMember, Sprint, Milestone, ProjectRisk, ProjectDocument


class ProjectMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMember
        fields = "__all__"
        read_only_fields = ["joined_at"]


class SprintSerializer(serializers.ModelSerializer):
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Sprint
        fields = "__all__"
        read_only_fields = ["created_at"]

    def get_task_count(self, obj):
        return obj.sprint_tasks.count()


class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = "__all__"
        read_only_fields = ["created_at"]


class ProjectRiskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectRisk
        fields = "__all__"
        read_only_fields = ["created_at"]


class ProjectDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectDocument
        fields = "__all__"
        read_only_fields = ["created_at"]


class ProjectSerializer(serializers.ModelSerializer):
    members = ProjectMemberSerializer(many=True, read_only=True)
    sprints = SprintSerializer(many=True, read_only=True)
    milestones = MilestoneSerializer(many=True, read_only=True)
    task_count = serializers.SerializerMethodField()
    completion_pct = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def get_task_count(self, obj):
        return obj.project_tasks.count()

    def get_completion_pct(self, obj):
        total = obj.project_tasks.count()
        if total == 0:
            return 0
        done = obj.project_tasks.filter(status="done").count()
        return round((done / total) * 100, 1)


class ProjectListSerializer(serializers.ModelSerializer):
    task_count = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    completion_pct = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "name", "key", "status", "methodology", "start_date",
            "end_date", "budget", "is_billable", "color", "owner_id",
            "task_count", "member_count", "completion_pct", "created_at",
        ]

    def get_task_count(self, obj):
        return obj.project_tasks.count()

    def get_member_count(self, obj):
        return obj.members.count()

    def get_completion_pct(self, obj):
        total = obj.project_tasks.count()
        if total == 0:
            return 0
        done = obj.project_tasks.filter(status="done").count()
        return round((done / total) * 100, 1)
