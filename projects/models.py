from django.db import models
import uuid
import json

# Create your models here.

class Project(models.Model):
    """Project model following PPIR structure"""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    problem = models.TextField()
    process = models.TextField()
    impact = models.TextField()
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    results = models.TextField()
    technologies = models.JSONField(default=list)
    skills = models.JSONField(default=list)
    category = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    view_count = models.IntegerField(default=0)
    live_demo_url = models.CharField(max_length=500, null=True, blank=True)
    github_url = models.CharField(max_length=500, null=True, blank=True)
    display_order = models.IntegerField(default=0, db_index=True)
    is_deleted = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    project_image = models.CharField(max_length=500, null=True, blank=True)
    gallery_images = models.JSONField(null=True, blank=True, default=list)
    project_slug = models.SlugField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
        return f"<Project(id={self.id}, title={self.title})>"

    def __repr__(self):
        return self.__str__()

    def get_technologies(self):
        """Get technologies list"""
        return self.technologies if self.technologies else []

    def set_technologies(self, tech_list):
        """Set technologies list"""
        self.technologies = tech_list if tech_list else []

    def get_gallery_images(self):
        """Get gallery images list"""
        return self.gallery_images if self.gallery_images else []

    def set_gallery_images(self, images_list):
        """Set gallery images list"""
        self.gallery_images = images_list if images_list else []

