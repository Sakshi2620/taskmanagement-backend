from django.utils import timezone
from rest_framework import serializers
from .models import User, Task
import datetime


class RegisterSerializer(serializers.ModelSerializer):
    password         = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        from .models import Profile
        Profile.objects.create(user=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'avatar_color', 'streak_count']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class TaskSerializer(serializers.ModelSerializer):
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model  = Task
        fields = [
            'id', 'title', 'description', 'notes', 'status', 'priority',
            'category', 'due_date', 'recurrence', 'order',
            'completed_at', 'created_at', 'updated_at', 'is_overdue'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at', 'is_overdue']

    def get_is_overdue(self, obj):
        if obj.due_date and obj.status != 'done':
            return obj.due_date < datetime.date.today()
        return False

    def update(self, instance, validated_data):
        # Auto-set completed_at when status changes to done
        if validated_data.get('status') == 'done' and instance.status != 'done':
            validated_data['completed_at'] = timezone.now()
        elif validated_data.get('status') != 'done' and instance.status == 'done':
            validated_data['completed_at'] = None
        return super().update(instance, validated_data)