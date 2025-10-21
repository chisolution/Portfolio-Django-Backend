import logging
from typing import Dict
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import RefreshToken
from uuid import UUID

from authentication.models import User
from authentication.services import UserService
from authentication.serializers import (
    UserCreateSerializer, UserDetailSerializer, UserUpdateSerializer,
    UserListSerializer, ChangePasswordSerializer, AuthenticationSerializer
)

logger = logging.getLogger(__name__)
service = UserService()


def get_tokens_for_user(user: User) -> Dict[str, str]:
    """Generate JWT tokens for a user.

    Args:
        user: User instance

    Returns:
        Dictionary with access and refresh tokens
    """
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    }


def standardized_response(
    message: str,
    data: dict = None,
    status_code: int = 200,
    http_status: int = None
) -> Response:
    """Create a standardized API response.

    Args:
        message: Response message
        data: Response data
        status_code: HTTP status code
        http_status: DRF HTTP status (defaults to status_code)

    Returns:
        Response object with standardized format
    """
    if http_status is None:
        http_status = status_code

    return Response({
        "message": message,
        "data": data or {},
        "status_code": status_code
    }, status=http_status)


@api_view(['POST'])
def register_user(request: Request) -> Response:
    """Register a new user.

    POST /api/v1/authentication/register/
    """
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = service.create_user(**serializer.validated_data)
            tokens = get_tokens_for_user(user)
            response_serializer = UserDetailSerializer(user)
            user_data = response_serializer.data
            user_data.update(tokens)

            return standardized_response(
                message="User registered successfully",
                data=user_data,
                status_code=201,
                http_status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return standardized_response(
                message="Registration failed",
                data={"error": str(e)},
                status_code=400,
                http_status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return standardized_response(
                message="An error occurred while creating the user",
                data={"error": str(e)},
                status_code=500,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return standardized_response(
        message="Validation failed",
        data={"errors": serializer.errors},
        status_code=400,
        http_status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
def authenticate_user(request: Request) -> Response:
    """Authenticate a user.

    POST /api/v1/authentication/login/
    """
    serializer = AuthenticationSerializer(data=request.data)
    if serializer.is_valid():
        user = service.authenticate(
            serializer.validated_data['username'],
            serializer.validated_data['password']
        )
        if user:
            tokens = get_tokens_for_user(user)
            response_serializer = UserDetailSerializer(user)
            user_data = response_serializer.data
            user_data.update(tokens)

            return standardized_response(
                message="Login successful",
                data=user_data,
                status_code=200,
                http_status=status.HTTP_200_OK
            )
        return standardized_response(
            message="Login failed",
            data={"error": "Invalid credentials"},
            status_code=401,
            http_status=status.HTTP_401_UNAUTHORIZED
        )
    return standardized_response(
        message="Validation failed",
        data={"errors": serializer.errors},
        status_code=400,
        http_status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def user_detail(request: Request, user_id: str) -> Response:
    """Get, update, or delete a user.

    GET /api/v1/authentication/users/{user_id}/
    PUT /api/v1/authentication/users/{user_id}/
    PATCH /api/v1/authentication/users/{user_id}/
    DELETE /api/v1/authentication/users/{user_id}/
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return standardized_response(
            message="Invalid user ID format",
            data={"error": "Invalid UUID format"},
            status_code=400,
            http_status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == 'GET':
        user = service.get_user(user_uuid)
        if not user:
            return standardized_response(
                message="User not found",
                data={"error": "User not found"},
                status_code=404,
                http_status=status.HTTP_404_NOT_FOUND
            )
        serializer = UserDetailSerializer(user)
        return standardized_response(
            message="User retrieved successfully",
            data=serializer.data,
            status_code=200,
            http_status=status.HTTP_200_OK
        )

    elif request.method in ['PUT', 'PATCH']:
        user = service.get_user(user_uuid)
        if not user:
            return standardized_response(
                message="User not found",
                data={"error": "User not found"},
                status_code=404,
                http_status=status.HTTP_404_NOT_FOUND
            )
        serializer = UserUpdateSerializer(data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            try:
                updated_user = service.update_user(user_uuid, **serializer.validated_data)
                response_serializer = UserDetailSerializer(updated_user)
                return standardized_response(
                    message="User updated successfully",
                    data=response_serializer.data,
                    status_code=200,
                    http_status=status.HTTP_200_OK
                )
            except Exception as e:
                logger.error(f"Error updating user: {str(e)}")
                return standardized_response(
                    message="An error occurred while updating the user",
                    data={"error": str(e)},
                    status_code=500,
                    http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return standardized_response(
            message="Validation failed",
            data={"errors": serializer.errors},
            status_code=400,
            http_status=status.HTTP_400_BAD_REQUEST
        )

    elif request.method == 'DELETE':
        if service.delete_user(user_uuid):
            return standardized_response(
                message="User deleted successfully",
                data={},
                status_code=204,
                http_status=status.HTTP_204_NO_CONTENT
            )
        return standardized_response(
            message="User not found",
            data={"error": "User not found"},
            status_code=404,
            http_status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def list_users(request: Request) -> Response:
    """List all users with pagination.

    GET /api/v1/authentication/users/
    Query params: page, page_size
    """
    page = request.query_params.get('page', 1)
    page_size = request.query_params.get('page_size', 10)

    try:
        page = int(page)
        page_size = int(page_size)
    except ValueError:
        return standardized_response(
            message="Invalid pagination parameters",
            data={"error": "Invalid page or page_size"},
            status_code=400,
            http_status=status.HTTP_400_BAD_REQUEST
        )

    try:
        paginated_data = service.get_paginated_users(page, page_size)
        users = paginated_data['items']
        serializer = UserListSerializer(users, many=True)
        return standardized_response(
            message="Users retrieved successfully",
            data={
                "count": paginated_data['total'],
                "page": page,
                "page_size": page_size,
                "total_pages": paginated_data.get('total_pages', 0),
                "results": serializer.data
            },
            status_code=200,
            http_status=status.HTTP_200_OK
        )
    except ValueError as e:
        return standardized_response(
            message="Error retrieving users",
            data={"error": str(e)},
            status_code=400,
            http_status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def change_password(request: Request, user_id: str) -> Response:
    """Change user password.

    POST /api/v1/authentication/users/{user_id}/change-password/
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return standardized_response(
            message="Invalid user ID format",
            data={"error": "Invalid UUID format"},
            status_code=400,
            http_status=status.HTTP_400_BAD_REQUEST
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
                return standardized_response(
                    message="Password changed successfully",
                    data={},
                    status_code=200,
                    http_status=status.HTTP_200_OK
                )
            return standardized_response(
                message="Password change failed",
                data={"error": "Invalid old password or user not found"},
                status_code=400,
                http_status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            return standardized_response(
                message="Password change failed",
                data={"error": str(e)},
                status_code=400,
                http_status=status.HTTP_400_BAD_REQUEST
            )
    return standardized_response(
        message="Validation failed",
        data={"errors": serializer.errors},
        status_code=400,
        http_status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
def activate_user_view(request: Request, user_id: str) -> Response:
    """Activate a user.

    POST /api/v1/authentication/users/{user_id}/activate/
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return standardized_response(
            message="Invalid user ID format",
            data={"error": "Invalid UUID format"},
            status_code=400,
            http_status=status.HTTP_400_BAD_REQUEST
        )

    if service.activate_user(user_uuid):
        user = service.get_user(user_uuid)
        serializer = UserDetailSerializer(user)
        return standardized_response(
            message="User activated successfully",
            data=serializer.data,
            status_code=200,
            http_status=status.HTTP_200_OK
        )
    return standardized_response(
        message="User not found",
        data={"error": "User not found"},
        status_code=404,
        http_status=status.HTTP_404_NOT_FOUND
    )


@api_view(['POST'])
def deactivate_user_view(request: Request, user_id: str) -> Response:
    """Deactivate a user.

    POST /api/v1/authentication/users/{user_id}/deactivate/
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return standardized_response(
            message="Invalid user ID format",
            data={"error": "Invalid UUID format"},
            status_code=400,
            http_status=status.HTTP_400_BAD_REQUEST
        )

    if service.deactivate_user(user_uuid):
        user = service.get_user(user_uuid)
        serializer = UserDetailSerializer(user)
        return standardized_response(
            message="User deactivated successfully",
            data=serializer.data,
            status_code=200,
            http_status=status.HTTP_200_OK
        )
    return standardized_response(
        message="User not found",
        data={"error": "User not found"},
        status_code=404,
        http_status=status.HTTP_404_NOT_FOUND
    )
