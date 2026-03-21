from rest_framework import serializers
from .models import TimeEntry, TimerSession, ResourceAllocation


class TimeEntrySerializer(serializers.ModelSerializer):
    amount = serializers.ReadOnlyField()

    class Meta:
        model = TimeEntry
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "user_id", "is_invoiced", "invoice_id"]


class TimerSessionSerializer(serializers.ModelSerializer):
    elapsed_minutes = serializers.SerializerMethodField()

    class Meta:
        model = TimerSession
        fields = "__all__"

    def get_elapsed_minutes(self, obj):
        from django.utils import timezone
        delta = timezone.now() - obj.started_at
        return round(delta.total_seconds() / 60, 1)


class ResourceAllocationSerializer(serializers.ModelSerializer):
    total_hours = serializers.SerializerMethodField()

    class Meta:
        model = ResourceAllocation
        fields = "__all__"
        read_only_fields = ["created_at"]

    def get_total_hours(self, obj):
        from datetime import timedelta
        days = (obj.end_date - obj.start_date).days + 1
        return float(obj.allocated_hours_per_day) * days
