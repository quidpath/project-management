from django.urls import path
from . import views

urlpatterns = [
    path("", views.NotificationListView.as_view()),
    path("<int:pk>/read/", views.MarkNotificationReadView.as_view()),
    path("mark-all-read/", views.mark_all_read),
]
