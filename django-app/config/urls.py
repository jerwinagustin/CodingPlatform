"""
URL configuration for django-app project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('api/professors/', include('professors.urls')),
    path('api/students/', include('students.urls')),
]
