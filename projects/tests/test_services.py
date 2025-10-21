"""Tests for Project Service"""
from django.test import TestCase
from django.db import connection
from django.test.utils import skipIf
from projects.models import Project
from projects.services import ProjectService


class ProjectServiceTests(TestCase):
    """Test cases for ProjectService"""

    def setUp(self):
        """Set up test data"""
        self.service = ProjectService()
        self.project = Project.objects.create(
            title='Test Project',
            description='This is a test project',
            problem='This is the problem',
            process='This is the process',
            impact='This is the impact',
            results='These are the results',
            project_slug='test-project'
        )

    def test_create_project_success(self):
        """Test creating a project successfully"""
        project = self.service.create_project(
            title='New Project',
            description='New Description',
            problem='New Problem',
            process='New Process',
            impact='New Impact',
            results='New Results',
            project_slug='new-project'
        )
        self.assertIsNotNone(project)
        self.assertEqual(project.title, 'New Project')

    def test_create_project_short_title(self):
        """Test creating project with short title"""
        with self.assertRaises(ValueError):
            self.service.create_project(
                title='AB',
                description='Description',
                problem='Problem',
                process='Process',
                impact='Impact',
                results='Results',
                project_slug='short-title'
            )

    def test_create_project_short_ppir_fields(self):
        """Test creating project with short PPIR fields"""
        with self.assertRaises(ValueError):
            self.service.create_project(
                title='Valid Title',
                description='Description',
                problem='Short',
                process='Process',
                impact='Impact',
                results='Results',
                project_slug='short-ppir'
            )

    def test_get_project(self):
        """Test getting a project"""
        project = self.service.get_project(self.project.id)
        self.assertIsNotNone(project)
        self.assertEqual(project.id, self.project.id)

    def test_get_project_by_slug(self):
        """Test getting project by slug"""
        project = self.service.get_project_by_slug('test-project')
        self.assertIsNotNone(project)
        self.assertEqual(project.project_slug, 'test-project')

    def test_get_all_projects(self):
        """Test getting all projects"""
        projects = self.service.get_all_projects()
        self.assertEqual(len(projects), 1)

    def test_get_published_projects(self):
        """Test getting published projects"""
        self.project.is_published = True
        self.project.save()
        projects = self.service.get_published_projects()
        self.assertEqual(len(projects), 1)

    def test_get_featured_projects(self):
        """Test getting featured projects"""
        self.project.is_published = True
        self.project.is_featured = True
        self.project.save()
        projects = self.service.get_featured_projects()
        self.assertEqual(len(projects), 1)

    def test_publish_project(self):
        """Test publishing a project"""
        result = self.service.publish_project(self.project.id)
        self.assertTrue(result)
        project = self.service.get_project(self.project.id)
        self.assertTrue(project.is_published)

    def test_unpublish_project(self):
        """Test unpublishing a project"""
        self.project.is_published = True
        self.project.save()
        result = self.service.unpublish_project(self.project.id)
        self.assertTrue(result)
        project = self.service.get_project(self.project.id)
        self.assertFalse(project.is_published)

    def test_feature_project(self):
        """Test featuring a project"""
        result = self.service.feature_project(self.project.id)
        self.assertTrue(result)
        project = self.service.get_project(self.project.id)
        self.assertTrue(project.is_featured)

    def test_unfeature_project(self):
        """Test unfeaturing a project"""
        self.project.is_featured = True
        self.project.save()
        result = self.service.unfeature_project(self.project.id)
        self.assertTrue(result)
        project = self.service.get_project(self.project.id)
        self.assertFalse(project.is_featured)

    def test_search_projects(self):
        """Test searching projects"""
        projects = self.service.search_projects('Test')
        self.assertEqual(len(projects), 1)

    def test_search_projects_short_query(self):
        """Test searching with short query"""
        with self.assertRaises(ValueError):
            self.service.search_projects('A')

    @skipIf(connection.vendor == 'sqlite', "SQLite doesn't support JSONField contains lookup")
    def test_search_projects_by_technology(self):
        """Test searching projects by technology"""
        self.project.technologies = ['Python', 'Django']
        self.project.is_published = True
        self.project.save()
        projects = self.service.get_projects_by_technology('Python')
        self.assertEqual(len(projects), 1)

    def test_hard_delete_project(self):
        """Test hard deleting project"""
        project_id = self.project.id
        result = self.service.hard_delete_project(project_id)
        self.assertTrue(result)
        project = self.service.get_project(project_id)
        self.assertIsNone(project)

    def test_soft_delete_project(self):
        """Test soft deleting project"""
        result = self.service.soft_delete_project(self.project.id)
        self.assertTrue(result)
        project = self.service.get_project(self.project.id)
        self.assertTrue(project.is_deleted)

    def test_get_project_statistics(self):
        """Test getting project statistics"""
        stats = self.service.get_project_statistics()
        self.assertIn('total', stats)
        self.assertIn('published', stats)
        self.assertIn('featured', stats)

    def test_get_paginated_projects(self):
        """Test getting paginated projects"""
        self.project.is_published = True
        self.project.save()
        result = self.service.get_paginated_projects(1, 10)
        self.assertIn('total', result)
        self.assertIn('items', result)
        self.assertEqual(result['total'], 1)

    def test_update_project(self):
        """Test updating project"""
        project = self.service.update_project(
            self.project.id,
            title='Updated Title'
        )
        self.assertIsNotNone(project)
        self.assertEqual(project.title, 'Updated Title')

    def test_get_filtered_projects_by_category(self):
        """Test filtering projects by category"""
        self.project.category = 'Web Development'
        self.project.is_published = True
        self.project.save()

        result = self.service.get_filtered_projects(
            page=1,
            page_size=10,
            published_only=True,
            category='Web Development'
        )
        self.assertEqual(result['total'], 1)
        self.assertEqual(len(result['items']), 1)

    def test_get_filtered_projects_by_status(self):
        """Test filtering projects by status"""
        self.project.status = 'completed'
        self.project.is_published = True
        self.project.save()

        result = self.service.get_filtered_projects(
            page=1,
            page_size=10,
            published_only=True,
            status='completed'
        )
        self.assertEqual(result['total'], 1)

    @skipIf(connection.vendor == 'sqlite', 'SQLite does not support JSONField contains lookup')
    def test_get_filtered_projects_by_technology(self):
        """Test filtering projects by technology"""
        self.project.technologies = ['Python', 'Django']
        self.project.is_published = True
        self.project.save()

        result = self.service.get_filtered_projects(
            page=1,
            page_size=10,
            published_only=True,
            technologies=['Python']
        )
        self.assertEqual(result['total'], 1)

    @skipIf(connection.vendor == 'sqlite', 'SQLite does not support JSONField contains lookup')
    def test_get_filtered_projects_by_skills(self):
        """Test filtering projects by skills"""
        self.project.skills = ['REST API', 'Database Design']
        self.project.is_published = True
        self.project.save()

        result = self.service.get_filtered_projects(
            page=1,
            page_size=10,
            published_only=True,
            skills=['REST API']
        )
        self.assertEqual(result['total'], 1)

    def test_get_project_statistics_includes_view_count(self):
        """Test that project statistics includes view_count"""
        self.project.view_count = 100
        self.project.save()

        stats = self.service.get_project_statistics()
        self.assertIn('total_views', stats)
        self.assertEqual(stats['total_views'], 100)

