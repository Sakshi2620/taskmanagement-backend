from django.db import models
from django.contrib.auth.models import AbstractUser


# Custom User model — required because settings.py sets AUTH_USER_MODEL = "tasks.User"
class User(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile({self.user.username})"


class Task(models.Model):
    STATUS_CHOICES = [
        ('todo',        'To Do'),
        ('in_progress', 'In Progress'),
        ('done',        'Done'),
    ]

    owner       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} [{self.owner.username}]"