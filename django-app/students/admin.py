from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'email', 'first_name', 'last_name', 'program', 'year', 'is_active', 'created_at']
    list_filter = ['is_active', 'program', 'year', 'created_at']
    search_fields = ['student_id', 'email', 'first_name', 'last_name']
    readonly_fields = ['created_at', 'updated_at']
