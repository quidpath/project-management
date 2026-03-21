from rest_framework import serializers
from .models import Task, TaskComment, TaskAttachment, TaskDependency, TaskLabel, Column, TaskWatcher


class TaskLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskLabel
        fields = "__all__"


class ColumnSerializer(serializers.ModelSerializer):
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Column
        fields = "__all__"

    def get_task_count(self, obj):
        return obj.column_tasks.count()


class TaskCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskComment
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "author_id"]


class TaskAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAttachment
        fields = "__all__"
        read_only_fields = ["created_at", "uploaded_by_id"]


class TaskDependencySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskDependency
        fields = "__all__"


class TaskWatcherSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskWatcher
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    subtask_count = serializers.SerializerMethodField()
    logged_hours = serializers.SerializerMethodField()
    labels = TaskLabelSerializer(many=True, read_only=True)
    label_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=TaskLabel.objects.all(), write_only=True, source="labels", required=False
    )

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["task_number", "created_at", "updated_at"]

    def get_subtask_count(self, obj):
        return obj.subtasks.count()

    def get_logged_hours(self, obj):
        from django.db.models import Sum
        if hasattr(obj, "time_entries"):
            result = obj.time_entries.aggregate(total=Sum("hours"))["total"]
            return float(result) if result else 0
        return 0


class TaskListSerializer(serializers.ModelSerializer):
    labels = TaskLabelSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            "id", "task_number", "title", "task_type", "priority", "status",
            "assignee_id", "due_date", "story_points", "progress", "labels",
            "sprint_id", "column_id", "parent_id", "order", "created_at",
        ]


class KanbanColumnSerializer(serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Column
        fields = ["id", "name", "order", "wip_limit", "is_done_column", "tasks"]

    def get_tasks(self, obj):
        tasks = obj.column_tasks.select_related("project").prefetch_related("labels").order_by("order")
        return TaskListSerializer(tasks, many=True).data
