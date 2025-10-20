"""Auth Serializers - Request/Response Validation"""
from rest_framework import serializers
from authentication.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, data):
        """Validate that passwords match"""
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

    def create(self, validated_data):
        """Create user with hashed password"""
        user = User.objects.create_user(**validated_data)
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for user details (read-only)"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information"""
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, required=True, min_length=8)

    def validate(self, data):
        """Validate that new passwords match"""
        if data['new_password'] != data.pop('new_password_confirm'):
            raise serializers.ValidationError({"new_password": "Passwords do not match"})
        return data


class AuthenticationSerializer(serializers.Serializer):
    """Serializer for user authentication"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
