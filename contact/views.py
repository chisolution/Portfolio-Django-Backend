"""Contact Views - Function-Based Views for Contact Management"""
import logging
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
            return Response(
                {"error": "Invalid page or page_size"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            paginated_data = service.get_paginated_contacts(page, page_size)
            contacts = paginated_data['items']

            # Filter by status if provided
            if status_filter:
                contacts = [c for c in contacts if c.status == status_filter]

            serializer = ContactListSerializer(contacts, many=True)
            return Response({
                "count": len(contacts),
                "page": page,
                "page_size": page_size,
                "results": serializer.data
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error creating contact: {str(e)}")
                return Response(
                    {"error": "An error occurred while creating the contact"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        return Response(
            {"error": "Invalid contact ID format"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == 'GET':
        contact = service.get_contact(contact_uuid)
        if not contact:
            return Response(
                {"error": "Contact not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ContactDetailSerializer(contact)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        contact = service.get_contact(contact_uuid)
        if not contact:
            return Response(
                {"error": "Contact not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ContactUpdateSerializer(data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            try:
                updated_contact = service.update_contact_status(
                    contact_uuid,
                    serializer.validated_data['status']
                )
                response_serializer = ContactDetailSerializer(updated_contact)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error updating contact: {str(e)}")
                return Response(
                    {"error": "An error occurred while updating the contact"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if service.delete_contact(contact_uuid):
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "Contact not found"},
            status=status.HTTP_404_NOT_FOUND
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
        return Response(
            {"error": "Query parameter is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        contacts = service.search_contacts(query)

        # Filter by status if provided
        if status_filter:
            contacts = [c for c in contacts if c.status == status_filter]

        serializer = ContactListSerializer(contacts, many=True)
        return Response({
            "count": len(contacts),
            "results": serializer.data
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def contact_statistics(request: Request) -> Response:
    """Get contact statistics.

    GET /api/v1/contact/statistics/
    """
    try:
        stats = service.get_contact_statistics()
        return Response(stats, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting contact statistics: {str(e)}")
        return Response(
            {"error": "An error occurred while getting statistics"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
