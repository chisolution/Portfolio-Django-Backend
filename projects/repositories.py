"""Project Repository Layer - Data Access Abstraction"""
import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

from django.db.models import QuerySet, Q
from projects.models import Project

logger = logging.getLogger(__name__)


class ProjectRepository:
    """Repository for Project model - handles all database operations"""

    @staticmethod
    def create(
        title: str,
        description: str,
        problem: str,
        process: str,
        impact: str,
        results: str,
        project_slug: str,
        technologies: Optional[List[str]] = None,
        start_date=None,
        end_date=None,
        live_demo_url: Optional[str] = None,
        github_url: Optional[str] = None,
        project_image: Optional[str] = None,
        gallery_images: Optional[List[str]] = None,
        display_order: int = 0,
        is_published: bool = False,
        is_featured: bool = False
    ) -> Project:
        """Create a new project.

        Args:
            title: Project title
            description: Project description
            problem: Problem statement (PPIR)
            process: Process description (PPIR)
            impact: Impact description (PPIR)
            results: Results/metrics
            project_slug: URL-friendly slug
            technologies: List of technologies used
            start_date: Project start date
            end_date: Project end date
            live_demo_url: URL to live demo
            github_url: URL to GitHub repository
            project_image: Main project image URL
            gallery_images: List of gallery image URLs
            display_order: Display order in list
            is_published: Whether project is published
            is_featured: Whether project is featured

        Returns:
            Project: The created project instance
        """
        try:
            project = Project.objects.create(
                title=title,
                description=description,
                problem=problem,
                process=process,
                impact=impact,
                results=results,
                project_slug=project_slug,
                technologies=technologies or [],
                start_date=start_date,
                end_date=end_date,
                live_demo_url=live_demo_url,
                github_url=github_url,
                project_image=project_image,
                gallery_images=gallery_images or [],
                display_order=display_order,
                is_published=is_published,
                is_featured=is_featured
            )
            logger.info(f"Project created: {project.id}")
            return project
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            raise

    @staticmethod
    def get_by_id(project_id: UUID) -> Optional[Project]:
        """Get a project by ID.

        Args:
            project_id: UUID of the project

        Returns:
            Project or None if not found
        """
        try:
            return Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            logger.warning(f"Project not found: {project_id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving project: {str(e)}")
            raise

    @staticmethod
    def get_by_slug(slug: str) -> Optional[Project]:
        """Get a project by slug.

        Args:
            slug: Project slug

        Returns:
            Project or None if not found
        """
        try:
            return Project.objects.get(project_slug=slug)
        except Project.DoesNotExist:
            logger.warning(f"Project not found with slug: {slug}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving project by slug: {str(e)}")
            raise

    @staticmethod
    def get_all() -> QuerySet:
        """Get all projects.

        Returns:
            QuerySet of all projects ordered by display order
        """
        return Project.objects.filter(is_deleted=False).order_by('display_order', '-created_at')

    @staticmethod
    def get_published() -> QuerySet:
        """Get all published projects.

        Returns:
            QuerySet of published projects ordered by display order
        """
        return Project.objects.filter(
            is_deleted=False,
            is_published=True
        ).order_by('display_order', '-created_at')

    @staticmethod
    def get_featured() -> QuerySet:
        """Get all featured projects.

        Returns:
            QuerySet of featured projects ordered by display order
        """
        return Project.objects.filter(
            is_deleted=False,
            is_published=True,
            is_featured=True
        ).order_by('display_order', '-created_at')

    @staticmethod
    def get_by_technology(technology: str) -> QuerySet:
        """Get projects that use a specific technology.

        Args:
            technology: Technology name to search for

        Returns:
            QuerySet of projects using the technology
        """
        return Project.objects.filter(
            is_deleted=False,
            is_published=True,
            technologies__contains=[technology]
        ).order_by('display_order', '-created_at')

    @staticmethod
    def search(query: str) -> QuerySet:
        """Search projects by title, description, or problem.

        Args:
            query: Search query string

        Returns:
            QuerySet of matching projects
        """
        return Project.objects.filter(
            Q(is_deleted=False) &
            (Q(title__icontains=query) |
             Q(description__icontains=query) |
             Q(problem__icontains=query))
        ).order_by('display_order', '-created_at')

    @staticmethod
    def update(project_id: UUID, **kwargs) -> Optional[Project]:
        """Update a project.

        Args:
            project_id: UUID of the project to update
            **kwargs: Fields to update

        Returns:
            Updated Project or None if not found
        """
        try:
            project = Project.objects.get(id=project_id)
            for key, value in kwargs.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            project.save()
            logger.info(f"Project updated: {project_id}")
            return project
        except Project.DoesNotExist:
            logger.warning(f"Project not found for update: {project_id}")
            return None
        except Exception as e:
            logger.error(f"Error updating project: {str(e)}")
            raise

    @staticmethod
    def soft_delete(project_id: UUID) -> bool:
        """Soft delete a project (mark as deleted).

        Args:
            project_id: UUID of the project to delete

        Returns:
            True if deleted, False if not found
        """
        try:
            project = Project.objects.get(id=project_id)
            project.is_deleted = True
            project.save()
            logger.info(f"Project soft deleted: {project_id}")
            return True
        except Project.DoesNotExist:
            logger.warning(f"Project not found for deletion: {project_id}")
            return False
        except Exception as e:
            logger.error(f"Error deleting project: {str(e)}")
            raise

    @staticmethod
    def hard_delete(project_id: UUID) -> bool:
        """Hard delete a project (permanently remove).

        Args:
            project_id: UUID of the project to delete

        Returns:
            True if deleted, False if not found
        """
        try:
            project = Project.objects.get(id=project_id)
            project.delete()
            logger.info(f"Project hard deleted: {project_id}")
            return True
        except Project.DoesNotExist:
            logger.warning(f"Project not found for hard deletion: {project_id}")
            return False
        except Exception as e:
            logger.error(f"Error hard deleting project: {str(e)}")
            raise

    @staticmethod
    def get_paginated(page: int = 1, page_size: int = 10, published_only: bool = True) -> Dict[str, Any]:
        """Get paginated projects.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            published_only: Whether to return only published projects

        Returns:
            Dictionary with paginated data and metadata
        """
        if published_only:
            queryset = Project.objects.filter(is_deleted=False, is_published=True)
        else:
            queryset = Project.objects.filter(is_deleted=False)

        total_count = queryset.count()
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        projects = queryset.order_by('display_order', '-created_at')[start_idx:end_idx]

        return {
            'items': list(projects),
            'total': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        }

    @staticmethod
    def count_published() -> int:
        """Count published projects.

        Returns:
            Number of published projects
        """
        return Project.objects.filter(is_deleted=False, is_published=True).count()

    @staticmethod
    def count_featured() -> int:
        """Count featured projects.

        Returns:
            Number of featured projects
        """
        return Project.objects.filter(is_deleted=False, is_published=True, is_featured=True).count()
