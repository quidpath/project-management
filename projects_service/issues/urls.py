from django.urls import path
from . import views

urlpatterns = [
    path("<int:project_pk>/categories/", views.IssueCategoryListCreateView.as_view()),
    path("<int:project_pk>/", views.IssueListCreateView.as_view()),
    path("<int:project_pk>/<int:pk>/", views.IssueDetailView.as_view()),
    path("<int:project_pk>/<int:issue_pk>/comments/", views.IssueCommentListView.as_view()),
    path("<int:project_pk>/<int:issue_pk>/attachments/", views.IssueAttachmentListView.as_view()),
]
