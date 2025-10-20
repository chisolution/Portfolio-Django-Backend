"""Auth Views - Function-Based Views for User Management"""
import logging
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from uuid import UUID

from authentication.models import User
from authentication.services import UserService
from authentication.serializers import (
    UserCreateSerializer, UserDetailSerializer, UserUpdateSerializer,
    UserListSerializer, ChangePasswordSerializer, AuthenticationSerializer
)

logger = logging.getLogger(__name__)
service = UserService()


@api_view(['POST'])
def register_user(request: Request) -> Response:
    """Register a new user.

    POST /api/v1/auth/register/
    """
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = service.create_user(**serializer.validated_data)
            response_serializer = UserDetailSerializer(user)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return Response(
                {"error": "An error occurred while creating the user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def authenticate_user(request: Request) -> Response:
    """Authenticate a user.

    POST /api/v1/auth/login/
    """
    serializer = AuthenticationSerializer(data=request.data)
    if serializer.is_valid():
        user = service.authenticate(
            serializer.validated_data['username'],
            serializer.validated_data['password']
        )
        if user:
            response_serializer = UserDetailSerializer(user)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def user_detail(request: Request, user_id: str) -> Response:
    """Get, update, or delete a user.

    GET /api/v1/auth/users/{user_id}/
    PUT /api/v1/auth/users/{user_id}/
    PATCH /api/v1/auth/users/{user_id}/
    DELETE /api/v1/auth/users/{user_id}/
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return Response(
            {"error": "Invalid user ID format"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == 'GET':
        user = service.get_user(user_uuid)
        if not user:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        user = service.get_user(user_uuid)
        if not user:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = UserUpdateSerializer(data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            try:
                updated_user = service.update_user(user_uuid, **serializer.validated_data)
                response_serializer = UserDetailSerializer(updated_user)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error updating user: {str(e)}")
                return Response(
                    {"error": "An error occurred while updating the user"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if service.delete_user(user_uuid):
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def list_users(request: Request) -> Response:
    """List all users with pagination.

    GET /api/v1/auth/users/
    Query params: page, page_size
    """
    page = request.query_params.get('page', 1)
    page_size = request.query_params.get('page_size', 10)

    try:
        page = int(page)
        page_size = int(page_size)
    except ValueError:
        return Response(
            {"error": "Invalid page or page_size"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        paginated_data = service.get_paginated_users(page, page_size)
        users = paginated_data['items']
        serializer = UserListSerializer(users, many=True)
        return Response({
            "count": paginated_data['total'],
            "page": page,
            "page_size": page_size,
            "results": serializer.data
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def change_password(request: Request, user_id: str) -> Response:
    """Change user password.

    POST /api/v1/auth/users/{user_id}/change-password/
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return Response(
            {"error": "Invalid user ID format"},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        try:
            success = service.change_password(
                user_uuid,
                serializer.validated_data['old_password'],
                serializer.validated_data['new_password']
            )
            if success:
                return Response(
                    {"message": "Password changed successfully"},
                    status=status.HTTP_200_OK
                )
            return Response(
                {"error": "Invalid old password or user not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def activate_user_view(request: Request, user_id: str) -> Response:
    """Activate a user.

    POST /api/v1/auth/users/{user_id}/activate/
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return Response(
            {"error": "Invalid user ID format"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if service.activate_user(user_uuid):
        user = service.get_user(user_uuid)
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(
        {"error": "User not found"},
        status=status.HTTP_404_NOT_FOUND
    )


@api_view(['POST'])
def deactivate_user_view(request: Request, user_id: str) -> Response:
    """Deactivate a user.

    POST /api/v1/auth/users/{user_id}/deactivate/
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return Response(
            {"error": "Invalid user ID format"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if service.deactivate_user(user_uuid):
        user = service.get_user(user_uuid)
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(
        {"error": "User not found"},
        status=status.HTTP_404_NOT_FOUND
    )
