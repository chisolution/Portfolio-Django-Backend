"""Project Views - Function-Based Views for Project Management"""
import logging
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
            return Response(
                {"error": "Invalid page or page_size"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            paginated_data = service.get_paginated_projects(page, page_size, published_only)
            projects = paginated_data['items']
            serializer = ProjectListSerializer(projects, many=True)
            return Response({
                "count": paginated_data['total'],
                "page": page,
                "page_size": page_size,
                "results": serializer.data
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'POST':
        serializer = ProjectCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                project = service.create_project(**serializer.validated_data)
                response_serializer = ProjectDetailSerializer(project)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error creating project: {str(e)}")
                return Response(
                    {"error": "An error occurred while creating the project"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        return Response(
            {"error": "Invalid project ID format"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == 'GET':
        project = service.get_project(project_uuid)
        if not project:
            return Response(
                {"error": "Project not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProjectDetailSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        project = service.get_project(project_uuid)
        if not project:
            return Response(
                {"error": "Project not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProjectUpdateSerializer(data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            try:
                updated_project = service.update_project(project_uuid, **serializer.validated_data)
                response_serializer = ProjectDetailSerializer(updated_project)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error updating project: {str(e)}")
                return Response(
                    {"error": "An error occurred while updating the project"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if service.soft_delete_project(project_uuid):
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "Project not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def project_by_slug(request: Request, slug: str) -> Response:
    """Get a project by slug.

    GET /api/v1/projects/slug/{slug}/
    """
    project = service.get_project_by_slug(slug)
    if not project:
        return Response(
            {"error": "Project not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = ProjectPublishedSerializer(project)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def published_projects(request: Request) -> Response:
    """Get all published projects.

    GET /api/v1/projects/published/
    """
    projects = service.get_published_projects_for_display()
    serializer = ProjectPublishedSerializer([p for p in service.get_published_projects()], many=True)
    return Response({
        "count": len(projects),
        "results": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def featured_projects(request: Request) -> Response:
    """Get all featured projects.

    GET /api/v1/projects/featured/
    """
    projects = service.get_featured_projects_for_display()
    serializer = ProjectPublishedSerializer([p for p in service.get_featured_projects()], many=True)
    return Response({
        "count": len(projects),
        "results": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def project_search(request: Request) -> Response:
    """Search projects.

    GET /api/v1/projects/search/
    Query params: query, technology
    """
    query = request.query_params.get('query', '')
    technology = request.query_params.get('technology', '')

    if not query:
        return Response(
            {"error": "Query parameter is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        projects = service.search_projects(query)

        # Filter by technology if provided
        if technology:
            projects = [p for p in projects if technology in p.get_technologies()]

        serializer = ProjectListSerializer(projects, many=True)
        return Response({
            "count": len(projects),
            "results": serializer.data
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def publish_project(request: Request, project_id: str) -> Response:
    """Publish a project.

    POST /api/v1/projects/{project_id}/publish/
    """
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        return Response(
            {"error": "Invalid project ID format"},
            status=status.HTTP_400_BAD_REQUEST
        )

    project = service.publish_project(project_uuid)
    if not project:
        return Response(
            {"error": "Project not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = ProjectDetailSerializer(project)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def unpublish_project(request: Request, project_id: str) -> Response:
    """Unpublish a project.

    POST /api/v1/projects/{project_id}/unpublish/
    """
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        return Response(
            {"error": "Invalid project ID format"},
            status=status.HTTP_400_BAD_REQUEST
        )

    project = service.unpublish_project(project_uuid)
    if not project:
        return Response(
            {"error": "Project not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = ProjectDetailSerializer(project)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def feature_project(request: Request, project_id: str) -> Response:
    """Feature a project.

    POST /api/v1/projects/{project_id}/feature/
    """
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        return Response(
            {"error": "Invalid project ID format"},
            status=status.HTTP_400_BAD_REQUEST
        )

    project = service.feature_project(project_uuid)
    if not project:
        return Response(
            {"error": "Project not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = ProjectDetailSerializer(project)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def unfeature_project(request: Request, project_id: str) -> Response:
    """Unfeature a project.

    POST /api/v1/projects/{project_id}/unfeature/
    """
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        return Response(
            {"error": "Invalid project ID format"},
            status=status.HTTP_400_BAD_REQUEST
        )

    project = service.unfeature_project(project_uuid)
    if not project:
        return Response(
            {"error": "Project not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = ProjectDetailSerializer(project)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def project_statistics(request: Request) -> Response:
    """Get project statistics.

    GET /api/v1/projects/statistics/
    """
    try:
        stats = service.get_project_statistics()
        return Response(stats, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting project statistics: {str(e)}")
        return Response(
            {"error": "An error occurred while getting statistics"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
