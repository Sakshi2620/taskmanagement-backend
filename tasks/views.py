from django.contrib.auth import authenticate
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
 
from .models import Task
from .serializers import RegisterSerializer, UserSerializer, TaskSerializer
 
 
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
 
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Registration successful. Please log in."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
 
    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')
 
        if not username or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
 
        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )
 
        # get or create DRF token for this user
        token, _ = Token.objects.get_or_create(user=user)
 
        return Response({
            "token": token.key,
            "user": UserSerializer(user).data
        })
 
 
class LogoutView(APIView):
    def post(self, request):
        # delete the token → user is logged out on all devices
        request.user.auth_token.delete()
        return Response({"message": "Logged out."})
 
 
# ── Task CRUD (only the logged-in user's tasks) ─────────────
 
class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
 
    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)
 
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
 
 
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
 
    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)