"""Project Service Layer - Business Logic"""
import logging
from typing import Optional, Dict, Any, List
from uuid import UUID

from projects.models import Project
from projects.repositories import ProjectRepository

logger = logging.getLogger(__name__)


class ProjectService:
    """Service for Project business logic"""

    def __init__(self):
        """Initialize the service with repository"""
        self.repository = ProjectRepository()

    def create_project(
        self,
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
        """Create a new project with validation.

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

        Raises:
            ValueError: If validation fails
        """
        # Validate input
        self._validate_project_input(title, description, problem, process, impact, results, project_slug)

        # Create project
        project = self.repository.create(
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

        logger.info(f"Project created successfully: {project.id}")
        return project

    def get_project(self, project_id: UUID) -> Optional[Project]:
        """Get a project by ID.

        Args:
            project_id: UUID of the project

        Returns:
            Project or None if not found
        """
        return self.repository.get_by_id(project_id)

    def get_project_by_slug(self, slug: str) -> Optional[Project]:
        """Get a project by slug.

        Args:
            slug: Project slug

        Returns:
            Project or None if not found
        """
        return self.repository.get_by_slug(slug)

    def get_all_projects(self) -> List[Project]:
        """Get all projects.

        Returns:
            List of all projects
        """
        return list(self.repository.get_all())

    def get_published_projects(self) -> List[Project]:
        """Get all published projects.

        Returns:
            List of published projects
        """
        return list(self.repository.get_published())

    def get_featured_projects(self) -> List[Project]:
        """Get all featured projects.

        Returns:
            List of featured projects
        """
        return list(self.repository.get_featured())

    def get_projects_by_technology(self, technology: str) -> List[Project]:
        """Get projects that use a specific technology.

        Args:
            technology: Technology name to search for

        Returns:
            List of projects using the technology
        """
        if not technology or len(technology.strip()) < 1:
            raise ValueError("Technology name must not be empty")

        return list(self.repository.get_by_technology(technology))

    def search_projects(self, query: str) -> List[Project]:
        """Search projects by title, description, or problem.

        Args:
            query: Search query string

        Returns:
            List of matching projects
        """
        if not query or len(query.strip()) < 2:
            raise ValueError("Search query must be at least 2 characters")

        return list(self.repository.search(query))

    def update_project(self, project_id: UUID, **kwargs) -> Optional[Project]:
        """Update a project.

        Args:
            project_id: UUID of the project to update
            **kwargs: Fields to update

        Returns:
            Updated Project or None if not found
        """
        return self.repository.update(project_id, **kwargs)

    def publish_project(self, project_id: UUID) -> Optional[Project]:
        """Publish a project.

        Args:
            project_id: UUID of the project to publish

        Returns:
            Updated Project or None if not found
        """
        return self.repository.update(project_id, is_published=True)

    def unpublish_project(self, project_id: UUID) -> Optional[Project]:
        """Unpublish a project.

        Args:
            project_id: UUID of the project to unpublish

        Returns:
            Updated Project or None if not found
        """
        return self.repository.update(project_id, is_published=False)

    def feature_project(self, project_id: UUID) -> Optional[Project]:
        """Feature a project.

        Args:
            project_id: UUID of the project to feature

        Returns:
            Updated Project or None if not found
        """
        return self.repository.update(project_id, is_featured=True)

    def unfeature_project(self, project_id: UUID) -> Optional[Project]:
        """Unfeature a project.

        Args:
            project_id: UUID of the project to unfeature

        Returns:
            Updated Project or None if not found
        """
        return self.repository.update(project_id, is_featured=False)

    def soft_delete_project(self, project_id: UUID) -> bool:
        """Soft delete a project (mark as deleted).

        Args:
            project_id: UUID of the project to delete

        Returns:
            True if deleted, False if not found
        """
        return self.repository.soft_delete(project_id)

    def hard_delete_project(self, project_id: UUID) -> bool:
        """Hard delete a project (permanently remove).

        Args:
            project_id: UUID of the project to delete

        Returns:
            True if deleted, False if not found
        """
        return self.repository.hard_delete(project_id)

    def get_project_statistics(self) -> Dict[str, Any]:
        """Get project statistics.

        Returns:
            Dictionary with project statistics
        """
        return {
            'total': len(self.repository.get_all()),
            'published': self.repository.count_published(),
            'featured': self.repository.count_featured()
        }

    def get_paginated_projects(
        self,
        page: int = 1,
        page_size: int = 10,
        published_only: bool = True
    ) -> Dict[str, Any]:
        """Get paginated projects.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            published_only: Whether to return only published projects

        Returns:
            Dictionary with paginated data
        """
        if page < 1:
            raise ValueError("Page number must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("Page size must be between 1 and 100")

        return self.repository.get_paginated(page, page_size, published_only)

    def get_project_for_display(self, project_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a project formatted for display (published only).

        Args:
            project_id: UUID of the project

        Returns:
            Formatted project data or None if not found or not published
        """
        project = self.repository.get_by_id(project_id)
        if not project or not project.is_published:
            return None

        return self._format_project_for_display(project)

    def get_published_projects_for_display(self) -> List[Dict[str, Any]]:
        """Get all published projects formatted for display.

        Returns:
            List of formatted project data
        """
        projects = self.repository.get_published()
        return [self._format_project_for_display(p) for p in projects]

    def get_featured_projects_for_display(self) -> List[Dict[str, Any]]:
        """Get all featured projects formatted for display.

        Returns:
            List of formatted project data
        """
        projects = self.repository.get_featured()
        return [self._format_project_for_display(p) for p in projects]

    # Validation methods
    def _validate_project_input(
        self,
        title: str,
        description: str,
        problem: str,
        process: str,
        impact: str,
        results: str,
        project_slug: str
    ) -> None:
        """Validate project input.

        Args:
            title: Project title
            description: Project description
            problem: Problem statement
            process: Process description
            impact: Impact description
            results: Results/metrics
            project_slug: URL-friendly slug

        Raises:
            ValueError: If validation fails
        """
        if not title or len(title.strip()) < 3:
            raise ValueError("Title must be at least 3 characters")

        if len(title) > 255:
            raise ValueError("Title must not exceed 255 characters")

        if not description or len(description.strip()) < 10:
            raise ValueError("Description must be at least 10 characters")

        if not problem or len(problem.strip()) < 10:
            raise ValueError("Problem statement must be at least 10 characters")

        if not process or len(process.strip()) < 10:
            raise ValueError("Process description must be at least 10 characters")

        if not impact or len(impact.strip()) < 10:
            raise ValueError("Impact description must be at least 10 characters")

        if not results or len(results.strip()) < 5:
            raise ValueError("Results must be at least 5 characters")

        if not project_slug or len(project_slug.strip()) < 3:
            raise ValueError("Project slug must be at least 3 characters")

        if len(project_slug) > 255:
            raise ValueError("Project slug must not exceed 255 characters")

    # Formatting methods
    def _format_project_for_display(self, project: Project) -> Dict[str, Any]:
        """Format a project for display.

        Args:
            project: Project instance

        Returns:
            Formatted project data
        """
        return {
            'id': str(project.id),
            'title': project.title,
            'description': project.description,
            'problem': project.problem,
            'process': project.process,
            'impact': project.impact,
            'results': project.results,
            'technologies': project.get_technologies(),
            'live_demo_url': project.live_demo_url,
            'github_url': project.github_url,
            'project_image': project.project_image,
            'gallery_images': project.get_gallery_images(),
            'project_slug': project.project_slug,
            'is_featured': project.is_featured,
            'created_at': project.created_at.isoformat() if project.created_at else None,
            'updated_at': project.updated_at.isoformat() if project.updated_at else None
        }
