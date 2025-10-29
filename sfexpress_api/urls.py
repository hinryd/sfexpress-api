"""
URL configuration for sfexpress_api project.
"""
from django.contrib import admin
from django.urls import path, include
from api import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Frontend pages (at root)
    path('', views.home, name='home'),
    path('register', views.register_view, name='register'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('dashboard/api-keys/create', views.create_api_key_dashboard, name='create_api_key_dashboard'),
    path('dashboard/api-keys/<int:key_id>/delete', views.delete_api_key, name='delete_api_key'),

    # API endpoints
    path('api/', include('api.urls')),
]
