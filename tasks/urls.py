from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, MeView,
    ChangePasswordView, StatsView,
    TaskListCreateView, TaskDetailView, TaskReorderView, TaskExportView
)

urlpatterns = [
    # Auth
    path('auth/register/',        RegisterView.as_view()),
    path('auth/login/',           LoginView.as_view()),
    path('auth/logout/',          LogoutView.as_view()),
    path('auth/me/',              MeView.as_view()),
    path('auth/change-password/', ChangePasswordView.as_view()),

    # Stats
    path('stats/',                StatsView.as_view()),

    # Tasks
    path('tasks/',                TaskListCreateView.as_view()),
    path('tasks/reorder/',        TaskReorderView.as_view()),
    path('tasks/export/',         TaskExportView.as_view()),
    path('tasks/<int:pk>/',       TaskDetailView.as_view()),
]