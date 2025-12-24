from rest_framework import serializers
from .models import Student, Submission


class StudentRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = Student
        fields = ['student_id', 'email', 'password', 'password_confirm', 
                  'first_name', 'last_name', 'program', 'year', 'phone']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        
        if data['year'] < 1 or data['year'] > 5:
            raise serializers.ValidationError("Year must be between 1 and 5")
        
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        student = Student(**validated_data)
        student.set_password(password)
        student.save()
        return student


class StudentLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'student_id', 'email', 'first_name', 'last_name', 
                  'program', 'year', 'phone', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CodeRunSerializer(serializers.Serializer):
    """Serializer for running code (quick test)"""
    activity_id = serializers.IntegerField()
    code = serializers.CharField()
    language = serializers.CharField(default='python')
    input = serializers.CharField(required=False, allow_blank=True, default='')


class CodeSubmitSerializer(serializers.Serializer):
    """Serializer for submitting code (full grading)"""
    activity_id = serializers.IntegerField()
    code = serializers.CharField()
    language = serializers.CharField(default='python')


class SubmissionSerializer(serializers.ModelSerializer):
    """Serializer for submission results"""
    activity_title = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    passed_tests = serializers.ReadOnlyField()
    total_tests = serializers.ReadOnlyField()
    
    class Meta:
        model = Submission
        fields = [
            'id', 'student', 'activity', 'activity_title', 'student_name',
            'code', 'language', 'status', 'result', 'score',
            'test_results', 'output', 'error_message',
            'execution_time', 'memory_used', 'passed_tests', 'total_tests',
            'is_final', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'result', 'score', 'test_results',
            'output', 'error_message', 'execution_time', 'memory_used',
            'created_at', 'updated_at'
        ]
    
    def get_activity_title(self, obj):
        return obj.activity.title if obj.activity else None
    
    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}" if obj.student else None


class SubmissionStatusSerializer(serializers.Serializer):
    """Serializer for checking submission status"""
    submission_id = serializers.IntegerField()
    status = serializers.CharField()
    result = serializers.CharField()
    score = serializers.IntegerField()
    output = serializers.CharField()
    error = serializers.CharField()
    is_complete = serializers.BooleanField()

