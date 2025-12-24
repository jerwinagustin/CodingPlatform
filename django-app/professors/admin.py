from django.contrib import admin
from .models import Professor, Activity


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'email', 'first_name', 'last_name', 'department', 'is_active', 'created_at']
    list_filter = ['is_active', 'department', 'created_at']
    search_fields = ['employee_id', 'email', 'first_name', 'last_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['title', 'professor', 'difficulty', 'programming_language', 'is_active', 'due_date', 'created_at']
    list_filter = ['difficulty', 'programming_language', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'professor__first_name', 'professor__last_name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('professor', 'title', 'description', 'difficulty')
        }),
        ('Problem Details', {
            'fields': ('problem_statement', 'starter_code', 'expected_output', 'test_cases')
        }),
        ('Configuration', {
            'fields': ('programming_language', 'time_limit', 'is_active', 'due_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
