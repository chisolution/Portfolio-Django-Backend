"""Project Serializers - Request/Response Validation"""
from rest_framework import serializers
from projects.models import Project


class ProjectCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new project"""
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'problem', 'process', 'impact', 'results',
            'project_slug', 'technologies', 'start_date', 'end_date',
            'live_demo_url', 'github_url', 'project_image', 'gallery_images',
            'display_order', 'is_published', 'is_featured'
        ]

    def validate_title(self, value):
        """Validate title"""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters")
        if len(value) > 255:
            raise serializers.ValidationError("Title must not exceed 255 characters")
        return value

    def validate_description(self, value):
        """Validate description"""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters")
        return value

    def validate_problem(self, value):
        """Validate problem statement"""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Problem statement must be at least 10 characters")
        return value

    def validate_process(self, value):
        """Validate process description"""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Process description must be at least 10 characters")
        return value

    def validate_impact(self, value):
        """Validate impact description"""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Impact description must be at least 10 characters")
        return value

    def validate_results(self, value):
        """Validate results"""
        if not value or len(value.strip()) < 5:
            raise serializers.ValidationError("Results must be at least 5 characters")
        return value

    def validate_project_slug(self, value):
        """Validate project slug"""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("Project slug must be at least 3 characters")
        if len(value) > 255:
            raise serializers.ValidationError("Project slug must not exceed 255 characters")
        return value


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer for project details (read-only)"""
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'problem', 'process', 'impact', 'results',
            'project_slug', 'technologies', 'start_date', 'end_date',
            'live_demo_url', 'github_url', 'project_image', 'gallery_images',
            'display_order', 'is_published', 'is_featured', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating project information"""
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'problem', 'process', 'impact', 'results',
            'project_slug', 'technologies', 'start_date', 'end_date',
            'live_demo_url', 'github_url', 'project_image', 'gallery_images',
            'display_order', 'is_published', 'is_featured'
        ]


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for listing projects"""
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'project_slug', 'technologies',
            'project_image', 'is_featured', 'display_order', 'created_at'
        ]


class ProjectPublishedSerializer(serializers.ModelSerializer):
    """Serializer for published projects (public view)"""
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'problem', 'process', 'impact', 'results',
            'project_slug', 'technologies', 'live_demo_url', 'github_url',
            'project_image', 'gallery_images', 'is_featured'
        ]


class ProjectSearchSerializer(serializers.Serializer):
    """Serializer for project search"""
    query = serializers.CharField(required=True, min_length=2)
    technology = serializers.CharField(required=False, allow_blank=True)
    published_only = serializers.BooleanField(default=True)
