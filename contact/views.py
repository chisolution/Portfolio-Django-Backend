import logging
from typing import Dict
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from uuid import UUID

from contact.models import Contact
from contact.services import ContactService
from contact.serializers import (
    ContactCreateSerializer, ContactDetailSerializer, ContactUpdateSerializer,
    ContactListSerializer, ContactSearchSerializer
)

logger = logging.getLogger(__name__)
service = ContactService()


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
def contact_list_create(request: Request) -> Response:
    """List all contacts or create a new contact.

    GET /api/v1/contact/
    POST /api/v1/contact/
    Query params (GET): page, page_size, status
    """
    if request.method == 'GET':
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)
        status_filter = request.query_params.get('status', '')

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
            paginated_data = service.get_paginated_contacts(page, page_size)
            contacts = paginated_data['items']

            # Filter by status if provided
            if status_filter:
                contacts = [c for c in contacts if c.status == status_filter]

            serializer = ContactListSerializer(contacts, many=True)
            return standardized_response(
                message="Contacts retrieved successfully",
                data={
                    "count": len(contacts),
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
                message="Error retrieving contacts",
                data={"error": str(e)},
                status_code=400,
                http_status=status.HTTP_400_BAD_REQUEST
            )

    elif request.method == 'POST':
        serializer = ContactCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Get client IP
                client_ip = request.META.get('REMOTE_ADDR', '')
                user_agent = request.META.get('HTTP_USER_AGENT', '')

                contact = service.create_contact(
                    **serializer.validated_data,
                    ip_address=client_ip,
                    user_agent=user_agent
                )
                response_serializer = ContactDetailSerializer(contact)
                return standardized_response(
                    message="Contact created successfully",
                    data=response_serializer.data,
                    status_code=201,
                    http_status=status.HTTP_201_CREATED
                )
            except ValueError as e:
                return standardized_response(
                    message="Contact creation failed",
                    data={"error": str(e)},
                    status_code=400,
                    http_status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                logger.error(f"Error creating contact: {str(e)}")
                return standardized_response(
                    message="An error occurred while creating the contact",
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
def contact_detail(request: Request, contact_id: str) -> Response:
    """Get, update, or delete a contact.

    GET /api/v1/contact/{contact_id}/
    PUT /api/v1/contact/{contact_id}/
    PATCH /api/v1/contact/{contact_id}/
    DELETE /api/v1/contact/{contact_id}/
    """
    try:
        contact_uuid = UUID(contact_id)
    except ValueError:
        return standardized_response(
            message="Invalid contact ID format",
            data={"error": "Invalid UUID format"},
            status_code=400,
            http_status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == 'GET':
        contact = service.get_contact(contact_uuid)
        if not contact:
            return standardized_response(
                message="Contact not found",
                data={"error": "Contact not found"},
                status_code=404,
                http_status=status.HTTP_404_NOT_FOUND
            )
        serializer = ContactDetailSerializer(contact)
        return standardized_response(
            message="Contact retrieved successfully",
            data=serializer.data,
            status_code=200,
            http_status=status.HTTP_200_OK
        )

    elif request.method in ['PUT', 'PATCH']:
        contact = service.get_contact(contact_uuid)
        if not contact:
            return standardized_response(
                message="Contact not found",
                data={"error": "Contact not found"},
                status_code=404,
                http_status=status.HTTP_404_NOT_FOUND
            )
        serializer = ContactUpdateSerializer(data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            try:
                updated_contact = service.update_contact_status(
                    contact_uuid,
                    serializer.validated_data['status']
                )
                response_serializer = ContactDetailSerializer(updated_contact)
                return standardized_response(
                    message="Contact updated successfully",
                    data=response_serializer.data,
                    status_code=200,
                    http_status=status.HTTP_200_OK
                )
            except Exception as e:
                logger.error(f"Error updating contact: {str(e)}")
                return standardized_response(
                    message="An error occurred while updating the contact",
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
        if service.delete_contact(contact_uuid):
            return standardized_response(
                message="Contact deleted successfully",
                data={},
                status_code=204,
                http_status=status.HTTP_204_NO_CONTENT
            )
        return standardized_response(
            message="Contact not found",
            data={"error": "Contact not found"},
            status_code=404,
            http_status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def contact_search(request: Request) -> Response:
    """Search contacts.

    GET /api/v1/contact/search/
    Query params: query, status
    """
    query = request.query_params.get('query', '')
    status_filter = request.query_params.get('status', '')

    if not query:
        return standardized_response(
            message="Query parameter is required",
            data={"error": "Query parameter is required"},
            status_code=400,
            http_status=status.HTTP_400_BAD_REQUEST
        )

    try:
        contacts = service.search_contacts(query)

        # Filter by status if provided
        if status_filter:
            contacts = [c for c in contacts if c.status == status_filter]

        serializer = ContactListSerializer(contacts, many=True)
        return standardized_response(
            message="Contacts searched successfully",
            data={
                "count": len(contacts),
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


@api_view(['GET'])
def contact_statistics(request: Request) -> Response:
    """Get contact statistics.

    GET /api/v1/contact/statistics/
    """
    try:
        stats = service.get_contact_statistics()
        return standardized_response(
            message="Contact statistics retrieved successfully",
            data=stats,
            status_code=200,
            http_status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Error getting contact statistics: {str(e)}")
        return standardized_response(
            message="An error occurred while getting statistics",
            data={"error": str(e)},
            status_code=500,
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
