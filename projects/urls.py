"""Project URL Configuration"""
from django.urls import path
from .views import *

app_name = 'projects'

urlpatterns = [
    # Project endpoints
    path('', project_list_create, name='project-list-create'),
    path('slug/<str:slug>/', project_by_slug, name='project-by-slug'),
    path('published/', published_projects, name='published-projects'),
    path('featured/', featured_projects, name='featured-projects'),
    path('search/', project_search, name='project-search'),
    path('statistics/', project_statistics, name='project-statistics'),

    # Project action endpoints (must come before generic <str:project_id>/)
    path('<str:project_id>/publish/', publish_project, name='publish-project'),
    path('<str:project_id>/unpublish/', unpublish_project, name='unpublish-project'),
    path('<str:project_id>/feature/', feature_project, name='feature-project'),
    path('<str:project_id>/unfeature/', unfeature_project, name='unfeature-project'),

    # Generic project detail endpoint (must be last)
    path('<str:project_id>/', project_detail, name='project-detail'),
]
