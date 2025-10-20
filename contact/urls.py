"""Contact URL Configuration"""
from django.urls import path
from .views import *

app_name = 'contact'

urlpatterns = [
    # Contact endpoints
    path('', contact_list_create, name='contact-list-create'),
    path('search/', contact_search, name='contact-search'),
    path('statistics/', contact_statistics, name='contact-statistics'),
    path('<str:contact_id>/', contact_detail, name='contact-detail'),
]
