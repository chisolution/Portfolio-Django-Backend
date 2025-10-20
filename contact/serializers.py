"""Contact Serializers - Request/Response Validation"""
from rest_framework import serializers
from contact.models import Contact


class ContactCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new contact submission"""
    class Meta:
        model = Contact
        fields = [
            'full_name', 'email', 'phone_number', 'subject', 'message',
            'file_attached', 'preferred_contact_method', 'organization'
        ]

    def validate_email(self, value):
        """Validate email format"""
        if not value or '@' not in value:
            raise serializers.ValidationError("Invalid email address")
        return value

    def validate_full_name(self, value):
        """Validate full name"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Full name must be at least 2 characters")
        return value

    def validate_subject(self, value):
        """Validate subject"""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("Subject must be at least 3 characters")
        return value

    def validate_message(self, value):
        """Validate message"""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters")
        return value


class ContactDetailSerializer(serializers.ModelSerializer):
    """Serializer for contact details (read-only)"""
    user_agent_parsed = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = [
            'id', 'full_name', 'email', 'phone_number', 'subject', 'message',
            'file_attached', 'preferred_contact_method', 'organization', 'status',
            'ip_address', 'user_agent', 'user_agent_parsed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'ip_address', 'user_agent']

    def get_user_agent_parsed(self, obj):
        """Get parsed user agent"""
        return obj.get_user_agent()


class ContactUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating contact status"""
    class Meta:
        model = Contact
        fields = ['status']


class ContactListSerializer(serializers.ModelSerializer):
    """Serializer for listing contacts"""
    class Meta:
        model = Contact
        fields = [
            'id', 'full_name', 'email', 'subject', 'status',
            'created_at', 'updated_at'
        ]


class ContactSearchSerializer(serializers.Serializer):
    """Serializer for contact search"""
    query = serializers.CharField(required=True, min_length=2)
    status = serializers.ChoiceField(
        choices=['new', 'contacted', 'closed'],
        required=False,
        allow_blank=True
    )
