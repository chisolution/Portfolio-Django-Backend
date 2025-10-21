import logging
from typing import Dict
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from uuid import UUID

from projects.models import Project
from projects.services import ProjectService
from projects.serializers import (
    ProjectCreateSerializer, ProjectDetailSerializer, ProjectUpdateSerializer,
    ProjectListSerializer, ProjectPublishedSerializer, ProjectSearchSerializer
)

logger = logging.getLogger(__name__)
service = ProjectService()


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


@api_view(['GET', 'POST'])
def project_list_create(request: Request) -> Response:
    """List all projects or create a new project.

    GET /api/v1/projects/
    POST /api/v1/projects/
    Query params (GET): page, page_size, published_only
    """
    if request.method == 'GET':
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)
        published_only = request.query_params.get('published_only', 'true').lower() == 'true'

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
            paginated_data = service.get_paginated_projects(page, page_size, published_only)
            projects = paginated_data['items']
            serializer = ProjectListSerializer(projects, many=True)
            return standardized_response(
                message="Projects retrieved successfully",
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
                message="Error retrieving projects",
                data={"error": str(e)},
                status_code=400,
                http_status=status.HTTP_400_BAD_REQUEST
            )

    elif request.method == 'POST':
        serializer = ProjectCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                project = service.create_project(**serializer.validated_data)
                response_serializer = ProjectDetailSerializer(project)
                return standardized_response(
                    message="Project created successfully",
                    data=response_serializer.data,
                    status_code=201,
                    http_status=status.HTTP_201_CREATED
                )
            except ValueError as e:
                return standardized_response(
                    message="Project creation failed",
                    data={"error": str(e)},
                    status_code=400,
                    http_status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                logger.error(f"Error creating project: {str(e)}")
                return standardized_response(
                    message="An error occurred while creating the project",
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


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def project_detail(request: Request, project_id: str) -> Response:
    """Get, update, or delete a project.

    GET /api/v1/projects/{project_id}/
    PUT /api/v1/projects/{project_id}/
    PATCH /api/v1/projects/{project_id}/
    DELETE /api/v1/projects/{project_id}/
    """
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        return standardized_response(
            message="Invalid project ID format",
            data={"error": "Invalid UUID format"},
            status_code=400,
            http_status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == 'GET':
        project = service.get_project(project_uuid)
        if not project:
            return standardized_response(
                message="Project not found",
                data={"error": "Project not found"},
                status_code=404,
                http_status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProjectDetailSerializer(project)
        return standardized_response(
            message="Project retrieved successfully",
            data=serializer.data,
            status_code=200,
            http_status=status.HTTP_200_OK
        )

    elif request.method in ['PUT', 'PATCH']:
        project = service.get_project(project_uuid)
        if not project:
            return standardized_response(
                message="Project not found",
                data={"error": "Project not found"},
                status_code=404,
                http_status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProjectUpdateSerializer(data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            try:
                updated_project = service.update_project(project_uuid, **serializer.validated_data)
                response_serializer = ProjectDetailSerializer(updated_project)
                return standardized_response(
                    message="Project updated successfully",
                    data=response_serializer.data,
                    status_code=200,
                    http_status=status.HTTP_200_OK
                )
            except Exception as e:
                logger.error(f"Error updating project: {str(e)}")
                return standardized_response(
                    message="An error occurred while updating the project",
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
        if service.soft_delete_project(project_uuid):
            return standardized_response(
                message="Project deleted successfully",
                data={},
                status_code=204,
                http_status=status.HTTP_204_NO_CONTENT
            )
        return standardized_response(
            message="Project not found",
            data={"error": "Project not found"},
            status_code=404,
            http_status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def project_by_slug(request: Request, slug: str) -> Response:
    """Get a project by slug.

    GET /api/v1/projects/slug/{slug}/
    """
    project = service.get_project_by_slug(slug)
    if not project:
        return standardized_response(
            message="Project not found",
            data={"error": "Project not found"},
            status_code=404,
            http_status=status.HTTP_404_NOT_FOUND
        )
    serializer = ProjectPublishedSerializer(project)
    return standardized_response(
        message="Project retrieved successfully",
        data=serializer.data,
        status_code=200,
        http_status=status.HTTP_200_OK
    )


@api_view(['GET'])
def published_projects(request: Request) -> Response:
    """Get all published projects.

    GET /api/v1/projects/published/
    """
    projects = service.get_published_projects_for_display()
    serializer = ProjectPublishedSerializer([p for p in service.get_published_projects()], many=True)
    return standardized_response(
        message="Published projects retrieved successfully",
        data={
            "count": len(projects),
            "results": serializer.data
        },
        status_code=200,
        http_status=status.HTTP_200_OK
    )


@api_view(['GET'])
def featured_projects(request: Request) -> Response:
    """Get all featured projects.

    GET /api/v1/projects/featured/
    """
    projects = service.get_featured_projects_for_display()
    serializer = ProjectPublishedSerializer([p for p in service.get_featured_projects()], many=True)
    return standardized_response(
        message="Featured projects retrieved successfully",
        data={
            "count": len(projects),
            "results": serializer.data
        },
        status_code=200,
        http_status=status.HTTP_200_OK
    )


@api_view(['GET'])
def project_search(request: Request) -> Response:
    """Search projects.

    GET /api/v1/projects/search/
    Query params: query, technology
    """
    query = request.query_params.get('query', '')
    technology = request.query_params.get('technology', '')

    if not query:
        return standardized_response(
            message="Query parameter is required",
            data={"error": "Query parameter is required"},
            status_code=400,
            http_status=status.HTTP_400_BAD_REQUEST
        )

    try:
        projects = service.search_projects(query)

        # Filter by technology if provided
        if technology:
            projects = [p for p in projects if technology in p.get_technologies()]

        serializer = ProjectListSerializer(projects, many=True)
        return standardized_response(
            message="Projects searched successfully",
            data={
                "count": len(projects),
                "results": serializer.data
            },
            status_code=200,
            http_status=status.HTTP_200_OK
        )
    except ValueError as e:
        return standardized_response(
            message="Search failed",
            data={"error": str(e)},
            status_code=400,
            http_status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def publish_project(request: Request, project_id: str) -> Response:
    """Publish a project.

    POST /api/v1/projects/{project_id}/publish/
    """
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        return standardized_response(
            message="Invalid project ID format",
            data={"error": "Invalid UUID format"},
            status_code=400,
            http_status=status.HTTP_400_BAD_REQUEST
        )

    project = service.publish_project(project_uuid)
    if not project:
        return standardized_response(
            message="Project not found",
            data={"error": "Project not found"},
            status_code=404,
            http_status=status.HTTP_404_NOT_FOUND
        )
    serializer = ProjectDetailSerializer(project)
    return standardized_response(
        message="Project published successfully",
        data=serializer.data,
        status_code=200,
        http_status=status.HTTP_200_OK
    )


@api_view(['POST'])
def unpublish_project(request: Request, project_id: str) -> Response:
    """Unpublish a project.

    POST /api/v1/projects/{project_id}/unpublish/
    """
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        return standardized_response(
            message="Invalid project ID format",
            data={"error": "Invalid UUID format"},
            status_code=400,
            http_status=status.HTTP_400_BAD_REQUEST
        )

    project = service.unpublish_project(project_uuid)
    if not project:
        return standardized_response(
            message="Project not found",
            data={"error": "Project not found"},
            status_code=404,
            http_status=status.HTTP_404_NOT_FOUND
        )
    serializer = ProjectDetailSerializer(project)
    return standardized_response(
        message="Project unpublished successfully",
        data=serializer.data,
        status_code=200,
        http_status=status.HTTP_200_OK
    )


@api_view(['POST'])
def feature_project(request: Request, project_id: str) -> Response:
    """Feature a project.

    POST /api/v1/projects/{project_id}/feature/
    """
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        return standardized_response(
            message="Invalid project ID format",
            data={"error": "Invalid UUID format"},
            status_code=400,
            http_status=status.HTTP_400_BAD_REQUEST
        )

    project = service.feature_project(project_uuid)
    if not project:
        return standardized_response(
            message="Project not found",
            data={"error": "Project not found"},
            status_code=404,
            http_status=status.HTTP_404_NOT_FOUND
        )
    serializer = ProjectDetailSerializer(project)
    return standardized_response(
        message="Project featured successfully",
        data=serializer.data,
        status_code=200,
        http_status=status.HTTP_200_OK
    )


@api_view(['POST'])
def unfeature_project(request: Request, project_id: str) -> Response:
    """Unfeature a project.

    POST /api/v1/projects/{project_id}/unfeature/
    """
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        return standardized_response(
            message="Invalid project ID format",
            data={"error": "Invalid UUID format"},
            status_code=400,
            http_status=status.HTTP_400_BAD_REQUEST
        )

    project = service.unfeature_project(project_uuid)
    if not project:
        return standardized_response(
            message="Project not found",
            data={"error": "Project not found"},
            status_code=404,
            http_status=status.HTTP_404_NOT_FOUND
        )
    serializer = ProjectDetailSerializer(project)
    return standardized_response(
        message="Project unfeatured successfully",
        data=serializer.data,
        status_code=200,
        http_status=status.HTTP_200_OK
    )


@api_view(['GET'])
def project_statistics(request: Request) -> Response:
    """Get project statistics.

    GET /api/v1/projects/statistics/
    """
    try:
        stats = service.get_project_statistics()
        return standardized_response(
            message="Project statistics retrieved successfully",
            data=stats,
            status_code=200,
            http_status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Error getting project statistics: {str(e)}")
        return standardized_response(
            message="An error occurred while getting statistics",
            data={"error": str(e)},
            status_code=500,
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
