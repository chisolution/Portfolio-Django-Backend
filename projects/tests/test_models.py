"""Tests for Project Models"""
from django.test import TestCase
from projects.models import Project
import uuid


class ProjectModelTests(TestCase):
    """Test cases for Project model"""

    def setUp(self):
        """Set up test data"""
        self.project_data = {
            'title': 'Test Project',
            'description': 'This is a test project description',
            'problem': 'This is the problem statement',
            'process': 'This is the process description',
            'impact': 'This is the impact description',
            'results': 'These are the results',
            'project_slug': 'test-project'
        }

    def test_create_project(self):
        """Test creating a project"""
        project = Project.objects.create(**self.project_data)
        self.assertEqual(project.title, 'Test Project')
        self.assertEqual(project.project_slug, 'test-project')
        self.assertFalse(project.is_published)
        self.assertFalse(project.is_featured)

    def test_project_id_is_uuid(self):
        """Test that project ID is UUID"""
        project = Project.objects.create(**self.project_data)
        self.assertIsInstance(project.id, uuid.UUID)

    def test_project_string_representation(self):
        """Test project string representation"""
        project = Project.objects.create(**self.project_data)
        expected = f"<Project(id={project.id}, title={project.title})>"
        self.assertEqual(str(project), expected)

    def test_project_repr(self):
        """Test project repr"""
        project = Project.objects.create(**self.project_data)
        expected = f"<Project(id={project.id}, title={project.title})>"
        self.assertEqual(repr(project), expected)

    def test_project_timestamps(self):
        """Test project timestamps"""
        project = Project.objects.create(**self.project_data)
        self.assertIsNotNone(project.created_at)
        self.assertIsNotNone(project.updated_at)

    def test_project_technologies_default(self):
        """Test project technologies default is empty list"""
        project = Project.objects.create(**self.project_data)
        self.assertEqual(project.technologies, [])

    def test_project_get_technologies(self):
        """Test getting technologies"""
        project = Project.objects.create(
            **self.project_data,
            technologies=['Python', 'Django']
        )
        techs = project.get_technologies()
        self.assertEqual(len(techs), 2)
        self.assertIn('Python', techs)

    def test_project_set_technologies(self):
        """Test setting technologies"""
        project = Project.objects.create(**self.project_data)
        project.set_technologies(['React', 'Node.js'])
        self.assertEqual(len(project.technologies), 2)

    def test_project_gallery_images_default(self):
        """Test project gallery images default is empty list"""
        project = Project.objects.create(**self.project_data)
        self.assertEqual(project.gallery_images, [])

    def test_project_get_gallery_images(self):
        """Test getting gallery images"""
        project = Project.objects.create(
            **self.project_data,
            gallery_images=['img1.jpg', 'img2.jpg']
        )
        images = project.get_gallery_images()
        self.assertEqual(len(images), 2)

    def test_project_set_gallery_images(self):
        """Test setting gallery images"""
        project = Project.objects.create(**self.project_data)
        project.set_gallery_images(['img1.jpg', 'img2.jpg'])
        self.assertEqual(len(project.gallery_images), 2)

    def test_project_is_deleted_default(self):
        """Test project is_deleted default is False"""
        project = Project.objects.create(**self.project_data)
        self.assertFalse(project.is_deleted)

    def test_project_display_order_default(self):
        """Test project display_order default is 0"""
        project = Project.objects.create(**self.project_data)
        self.assertEqual(project.display_order, 0)

    def test_project_unique_slug(self):
        """Test that project slug must be unique"""
        Project.objects.create(**self.project_data)
        with self.assertRaises(Exception):
            Project.objects.create(**self.project_data)

    def test_project_ordering(self):
        """Test that projects are ordered by display_order then created_at"""
        project1_data = self.project_data.copy()
        project1_data['project_slug'] = 'proj1'
        project1 = Project.objects.create(**project1_data)

        project2_data = self.project_data.copy()
        project2_data['project_slug'] = 'proj2'
        project2_data['display_order'] = 1
        project2 = Project.objects.create(**project2_data)

        projects = list(Project.objects.all())
        self.assertEqual(projects[0].id, project1.id)
        self.assertEqual(projects[1].id, project2.id)

    def test_project_meta_verbose_name(self):
        """Test project meta verbose name"""
        self.assertEqual(Project._meta.verbose_name, 'Project')
        self.assertEqual(Project._meta.verbose_name_plural, 'Projects')

    def test_project_with_urls(self):
        """Test project with URLs"""
        project = Project.objects.create(
            **self.project_data,
            live_demo_url='https://example.com',
            github_url='https://github.com/example'
        )
        self.assertEqual(project.live_demo_url, 'https://example.com')
        self.assertEqual(project.github_url, 'https://github.com/example')

    def test_project_with_image(self):
        """Test project with image"""
        project = Project.objects.create(
            **self.project_data,
            project_image='https://example.com/image.jpg'
        )
        self.assertEqual(project.project_image, 'https://example.com/image.jpg')

    def test_project_published_and_featured(self):
        """Test project published and featured flags"""
        project = Project.objects.create(
            **self.project_data,
            is_published=True,
            is_featured=True
        )
        self.assertTrue(project.is_published)
        self.assertTrue(project.is_featured)

