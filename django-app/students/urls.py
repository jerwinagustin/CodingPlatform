from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.student_register, name='student_register'),
    path('login/', views.student_login, name='student_login'),
    path('profile/', views.student_profile, name='student_profile'),
    
    # Activities
    path('activities/', views.get_student_activities, name='get_student_activities'),
    path('activities/<int:activity_id>/', views.get_activity_detail, name='get_activity_detail'),
    
    # Code Execution
    path('code/run/', views.run_code, name='run_code'),
    path('code/submit/', views.submit_code, name='submit_code'),
    path('code/submit-sync/', views.submit_code_sync, name='submit_code_sync'),
    
    # Submissions
    path('submissions/', views.get_student_submissions, name='get_student_submissions'),
    path('submissions/<int:submission_id>/status/', views.get_submission_status, name='get_submission_status'),
    path('submissions/<int:submission_id>/ai-feedback/', views.get_ai_feedback, name='get_ai_feedback'),
]
