"""Tests for Project Views/APIs"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from projects.models import Project


class ProjectAPITests(TestCase):
    """Test cases for Project API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
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
        """Test successful project creation"""
        data = {
            'title': 'New Project',
            'description': 'New Description',
            'problem': 'New Problem',
            'process': 'New Process',
            'impact': 'New Impact',
            'results': 'New Results',
            'project_slug': 'new-project'
        }
        response = self.client.post('/api/v1/projects/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Project')

    def test_create_project_short_title(self):
        """Test project creation with short title"""
        data = {
            'title': 'AB',
            'description': 'Description',
            'problem': 'Problem',
            'process': 'Process',
            'impact': 'Impact',
            'results': 'Results',
            'project_slug': 'short'
        }
        response = self.client.post('/api/v1/projects/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_projects(self):
        """Test listing projects"""
        # Publish the project first since published_only=true by default
        self.project.is_published = True
        self.project.save()
        response = self.client.get('/api/v1/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_list_projects_pagination(self):
        """Test listing projects with pagination"""
        response = self.client.get('/api/v1/projects/?page=1&page_size=10')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_get_project_detail(self):
        """Test getting project details"""
        response = self.client.get(f'/api/v1/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Project')

    def test_get_project_detail_not_found(self):
        """Test getting non-existent project"""
        fake_id = '00000000-0000-0000-0000-000000000000'
        response = self.client.get(f'/api/v1/projects/{fake_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_project_detail_invalid_id(self):
        """Test getting project with invalid ID format"""
        response = self.client.get('/api/v1/projects/invalid-id/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_project_by_slug(self):
        """Test getting project by slug"""
        response = self.client.get(f'/api/v1/projects/slug/{self.project.project_slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Project')

    def test_get_published_projects(self):
        """Test getting published projects"""
        self.project.is_published = True
        self.project.save()
        response = self.client.get('/api/v1/projects/published/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_get_featured_projects(self):
        """Test getting featured projects"""
        self.project.is_published = True
        self.project.is_featured = True
        self.project.save()
        response = self.client.get('/api/v1/projects/featured/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_update_project_patch(self):
        """Test updating project with PATCH"""
        data = {'title': 'Updated Title'}
        response = self.client.patch(f'/api/v1/projects/{self.project.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

    def test_update_project_put(self):
        """Test updating project with PUT"""
        data = {
            'title': 'Updated Title',
            'description': 'Updated Description',
            'problem': 'Updated Problem',
            'process': 'Updated Process',
            'impact': 'Updated Impact',
            'results': 'Updated Results',
            'project_slug': 'updated-slug'
        }
        response = self.client.put(f'/api/v1/projects/{self.project.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_project(self):
        """Test deleting project"""
        response = self.client.delete(f'/api/v1/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_search_projects(self):
        """Test searching projects"""
        self.project.is_published = True
        self.project.save()
        response = self.client.get('/api/v1/projects/search/?query=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)

    def test_search_projects_no_query(self):
        """Test searching without query parameter"""
        response = self.client.get('/api/v1/projects/search/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_publish_project(self):
        """Test publishing project"""
        response = self.client.post(f'/api/v1/projects/{self.project.id}/publish/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_published'])

    def test_unpublish_project(self):
        """Test unpublishing project"""
        self.project.is_published = True
        self.project.save()
        response = self.client.post(f'/api/v1/projects/{self.project.id}/unpublish/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_published'])

    def test_feature_project(self):
        """Test featuring project"""
        response = self.client.post(f'/api/v1/projects/{self.project.id}/feature/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_featured'])

    def test_unfeature_project(self):
        """Test unfeaturing project"""
        self.project.is_featured = True
        self.project.save()
        response = self.client.post(f'/api/v1/projects/{self.project.id}/unfeature/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_featured'])

    def test_project_statistics(self):
        """Test getting project statistics"""
        response = self.client.get('/api/v1/projects/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data)

