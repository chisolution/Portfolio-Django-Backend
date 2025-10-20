"""Auth URL Configuration"""
from django.urls import path
from .views import *

app_name = 'authentication'

urlpatterns = [
    # Authentication endpoints
    path('register/', register_user, name='register'),
    path('login/', authenticate_user, name='login'),

    # User management endpoints
    path('users/', list_users, name='user-list'),
    path('users/<str:user_id>/', user_detail, name='user-detail'),
    path('users/<str:user_id>/change-password/', change_password, name='change-password'),
    path('users/<str:user_id>/activate/', activate_user_view, name='activate-user'),
    path('users/<str:user_id>/deactivate/', deactivate_user_view, name='deactivate-user'),
]
