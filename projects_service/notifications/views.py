from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        qs = Notification.objects.filter(recipient_id=self.request.user_id)
        unread_only = self.request.query_params.get("unread")
        if unread_only and unread_only.lower() == "true":
            qs = qs.filter(is_read=False)
        return qs


class MarkNotificationReadView(APIView):
    def post(self, request, pk):
        n = Notification.objects.filter(pk=pk, recipient_id=request.user_id).first()
        if not n:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        n.is_read = True
        n.save(update_fields=["is_read"])
        return Response(NotificationSerializer(n).data)


@api_view(["POST"])
def mark_all_read(request):
    Notification.objects.filter(recipient_id=request.user_id, is_read=False).update(is_read=True)
    return Response({"message": "All notifications marked as read"})
