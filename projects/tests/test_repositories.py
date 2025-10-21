"""Tests for Project Repository"""
from django.test import TestCase
from django.db import connection
from django.test.utils import skipIf
from projects.models import Project
from projects.repositories import ProjectRepository
import uuid


class ProjectRepositoryTests(TestCase):
    """Test cases for ProjectRepository"""

    def setUp(self):
        """Set up test data"""
        self.repo = ProjectRepository()
        self.project1 = Project.objects.create(
            title='Project 1',
            description='Description 1',
            problem='Problem 1',
            process='Process 1',
            impact='Impact 1',
            results='Results 1',
            project_slug='project-1',
            is_published=False
        )
        self.project2 = Project.objects.create(
            title='Project 2',
            description='Description 2',
            problem='Problem 2',
            process='Process 2',
            impact='Impact 2',
            results='Results 2',
            project_slug='project-2',
            is_published=True,
            is_featured=True
        )

    def test_create_project(self):
        """Test creating a project via repository"""
        project = self.repo.create(
            title='Project 3',
            description='Description 3',
            problem='Problem 3',
            process='Process 3',
            impact='Impact 3',
            results='Results 3',
            project_slug='project-3'
        )
        self.assertIsNotNone(project)
        self.assertEqual(project.title, 'Project 3')

    def test_get_by_id(self):
        """Test getting project by ID"""
        project = self.repo.get_by_id(self.project1.id)
        self.assertIsNotNone(project)
        self.assertEqual(project.id, self.project1.id)

    def test_get_by_id_not_found(self):
        """Test getting non-existent project by ID"""
        fake_id = uuid.uuid4()
        project = self.repo.get_by_id(fake_id)
        self.assertIsNone(project)

    def test_get_by_slug(self):
        """Test getting project by slug"""
        project = self.repo.get_by_slug('project-1')
        self.assertIsNotNone(project)
        self.assertEqual(project.project_slug, 'project-1')

    def test_get_by_slug_not_found(self):
        """Test getting non-existent project by slug"""
        project = self.repo.get_by_slug('nonexistent')
        self.assertIsNone(project)

    def test_get_all(self):
        """Test getting all projects"""
        projects = self.repo.get_all()
        self.assertEqual(len(projects), 2)

    def test_get_published(self):
        """Test getting published projects"""
        projects = self.repo.get_published()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].title, 'Project 2')

    def test_get_featured(self):
        """Test getting featured projects"""
        projects = self.repo.get_featured()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].title, 'Project 2')

    @skipIf(connection.vendor == 'sqlite', "SQLite doesn't support JSONField contains lookup")
    def test_get_by_technology(self):
        """Test getting projects by technology"""
        project = Project.objects.create(
            title='Tech Project',
            description='Description',
            problem='Problem',
            process='Process',
            impact='Impact',
            results='Results',
            project_slug='tech-project',
            technologies=['Python', 'Django'],
            is_published=True
        )
        projects = self.repo.get_by_technology('Python')
        self.assertEqual(len(projects), 1)

    def test_soft_delete_project(self):
        """Test soft deleting a project"""
        result = self.repo.soft_delete(self.project1.id)
        self.assertTrue(result)
        project = self.repo.get_by_id(self.project1.id)
        self.assertTrue(project.is_deleted)

    def test_hard_delete_project(self):
        """Test hard deleting a project"""
        project_id = self.project1.id
        result = self.repo.hard_delete(project_id)
        self.assertTrue(result)
        project = self.repo.get_by_id(project_id)
        self.assertIsNone(project)

    def test_search_projects(self):
        """Test searching projects"""
        projects = self.repo.search('Project 1')
        self.assertEqual(len(projects), 1)

    def test_update_project(self):
        """Test updating project"""
        project = self.repo.update(self.project1.id, title='Updated Title')
        self.assertIsNotNone(project)
        self.assertEqual(project.title, 'Updated Title')

    def test_get_paginated(self):
        """Test getting paginated projects"""
        result = self.repo.get_paginated(1, 10, published_only=False)
        self.assertEqual(result['total'], 2)
        self.assertEqual(len(result['items']), 2)

    def test_count_published(self):
        """Test counting published projects"""
        count = self.repo.count_published()
        self.assertEqual(count, 1)

    def test_count_featured(self):
        """Test counting featured projects"""
        count = self.repo.count_featured()
        self.assertEqual(count, 1)

    def test_get_paginated_published_only(self):
        """Test getting paginated published projects only"""
        result = self.repo.get_paginated(1, 10, published_only=True)
        self.assertEqual(result['total'], 1)

