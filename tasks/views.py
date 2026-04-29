import csv
import datetime
from django.contrib.auth import authenticate
from django.http import HttpResponse
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Task, User
from .serializers import (
    RegisterSerializer, UserSerializer,
    TaskSerializer, ChangePasswordSerializer
)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successful. Please log in."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')
        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if not user:
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        # Update streak
        today = datetime.date.today()
        if user.last_active_date == today - datetime.timedelta(days=1):
            user.streak_count += 1
        elif user.last_active_date != today:
            user.streak_count = 1
        user.last_active_date = today
        user.save(update_fields=['streak_count', 'last_active_date'])

        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class LogoutView(APIView):
    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Logged out."})


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        user = request.user
        allowed = ['first_name', 'last_name', 'email', 'avatar_color']
        for field in allowed:
            if field in request.data:
                setattr(user, field, request.data[field])
        user.save()
        return Response(UserSerializer(user).data)


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            # Re-create token after password change
            request.user.auth_token.delete()
            token = Token.objects.create(user=request.user)
            return Response({"message": "Password changed.", "token": token.key})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StatsView(APIView):
    def get(self, request):
        user = request.user
        all_tasks = Task.objects.filter(owner=user)
        today = datetime.date.today()
        week_start = today - datetime.timedelta(days=6)

        # Tasks completed per day for the last 7 days
        weekly = []
        for i in range(6, -1, -1):
            day = today - datetime.timedelta(days=i)
            count = all_tasks.filter(
                status='done',
                completed_at__date=day
            ).count()
            weekly.append({"date": day.strftime("%a"), "completed": count})

        today_done = all_tasks.filter(status='done', completed_at__date=today).count()
        today_total = all_tasks.filter(created_at__date=today).count() + all_tasks.filter(status__in=['todo', 'in_progress']).count()

        return Response({
            "total": all_tasks.count(),
            "done": all_tasks.filter(status='done').count(),
            "in_progress": all_tasks.filter(status='in_progress').count(),
            "todo": all_tasks.filter(status='todo').count(),
            "overdue": sum(1 for t in all_tasks if t.due_date and t.due_date < today and t.status != 'done'),
            "today_done": today_done,
            "today_total": max(today_total, today_done),
            "streak": user.streak_count,
            "weekly": weekly,
        })


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        qs = Task.objects.filter(owner=self.request.user)
        # Filters
        status_f   = self.request.query_params.get('status')
        priority_f = self.request.query_params.get('priority')
        category_f = self.request.query_params.get('category')
        due_f      = self.request.query_params.get('due')  # 'overdue' | 'today'
        search_f   = self.request.query_params.get('search')

        if status_f:   qs = qs.filter(status=status_f)
        if priority_f: qs = qs.filter(priority=priority_f)
        if category_f: qs = qs.filter(category=category_f)
        if search_f:   qs = qs.filter(title__icontains=search_f)
        if due_f == 'overdue':
            qs = qs.filter(due_date__lt=datetime.date.today()).exclude(status='done')
        elif due_f == 'today':
            qs = qs.filter(due_date=datetime.date.today())
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)


class TaskReorderView(APIView):
    """PATCH /api/tasks/reorder/  body: { order: [id1, id2, id3, ...] }"""
    def patch(self, request):
        ids = request.data.get('order', [])
        for idx, task_id in enumerate(ids):
            Task.objects.filter(id=task_id, owner=request.user).update(order=idx)
        return Response({"message": "Reordered."})


class TaskExportView(APIView):
    """GET /api/tasks/export/ — returns CSV file"""
    def get(self, request):
        tasks = Task.objects.filter(owner=request.user)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tasks.csv"'
        writer = csv.writer(response)
        writer.writerow(['Title', 'Status', 'Priority', 'Category', 'Due Date', 'Description', 'Notes', 'Created'])
        for t in tasks:
            writer.writerow([
                t.title, t.status, t.priority, t.category,
                t.due_date or '', t.description, t.notes,
                t.created_at.strftime('%Y-%m-%d')
            ])
        return response