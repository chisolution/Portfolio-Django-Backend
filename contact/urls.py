from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

app_name = 'contact'

urlpatterns = [
    # Contact endpoints
    path('', contact_list_create, name='contact-list-create'),
    path('search/', contact_search, name='contact-search'),
    path('statistics/', contact_statistics, name='contact-statistics'),
    path('<str:contact_id>/', contact_detail, name='contact-detail'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
