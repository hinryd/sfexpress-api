from django.urls import path
from . import views

urlpatterns = [
    # API endpoints (JSON - require API key authentication)
    path('locations', views.locations, name='locations'),
]
