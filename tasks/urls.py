from django.urls import path
from .views import RegisterView, LoginView, LogoutView, TaskListCreateView, TaskDetailView
 
urlpatterns = [
    # auth
    path('auth/register/', RegisterView.as_view(),  name='register'),
    path('auth/login/',    LoginView.as_view(),     name='login'),
    path('auth/logout/',   LogoutView.as_view(),    name='logout'),
 
    # tasks  (require token in header: Authorization: Token <token>)
    path('tasks/',         TaskListCreateView.as_view(), name='task-list'),
    path('tasks/<int:pk>/',TaskDetailView.as_view(),     name='task-detail'),
]