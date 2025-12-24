from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.professor_register, name='professor_register'),
    path('login/', views.professor_login, name='professor_login'),
    path('profile/', views.professor_profile, name='professor_profile'),
    
    # Activity management endpoints
    path('activities/', views.list_activities, name='list_activities'),
    path('activities/create/', views.create_activity, name='create_activity'),
    path('activities/<int:activity_id>/', views.get_activity, name='get_activity'),
    path('activities/<int:activity_id>/update/', views.update_activity, name='update_activity'),
    path('activities/<int:activity_id>/delete/', views.delete_activity, name='delete_activity'),
]
