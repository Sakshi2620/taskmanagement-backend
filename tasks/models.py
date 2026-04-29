from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    avatar_color = models.CharField(max_length=7, default="#6366f1")
    streak_count = models.IntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile({self.user.username})"


class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    CATEGORY_CHOICES = [
        ('work', 'Work'),
        ('personal', 'Personal'),
        ('shopping', 'Shopping'),
        ('health', 'Health'),
        ('finance', 'Finance'),
        ('other', 'Other'),
    ]
    RECURRENCE_CHOICES = [
        ('none', 'None'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    owner        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title        = models.CharField(max_length=255)
    description  = models.TextField(blank=True)
    notes        = models.TextField(blank=True)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority     = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    category     = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    due_date     = models.DateField(null=True, blank=True)
    recurrence   = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, default='none')
    order        = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.title} [{self.owner.username}]"