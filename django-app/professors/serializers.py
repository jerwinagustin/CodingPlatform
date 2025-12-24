from rest_framework import serializers
from .models import Professor, Activity


class ProfessorRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = Professor
        fields = ['employee_id', 'email', 'password', 'password_confirm', 
                  'first_name', 'last_name', 'department', 'phone']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        professor = Professor(**validated_data)
        professor.set_password(password)
        professor.save()
        return professor


class ProfessorLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = ['id', 'employee_id', 'email', 'first_name', 'last_name', 
                  'department', 'phone', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ActivitySerializer(serializers.ModelSerializer):
    professor_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Activity
        fields = [
            'id', 'professor', 'professor_name', 'title', 'description',
            'problem_statement', 'starter_code', 'expected_output', 
            'test_cases', 'difficulty', 'time_limit', 'programming_language',
            'is_active', 'due_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_professor_name(self, obj):
        return f"{obj.professor.first_name} {obj.professor.last_name}"
    
    def validate_test_cases(self, value):
        """Validate that test_cases is a proper list of test case objects"""
        if not isinstance(value, list):
            raise serializers.ValidationError("test_cases must be a list")
        
        for i, test_case in enumerate(value):
            if not isinstance(test_case, dict):
                raise serializers.ValidationError(f"Test case {i+1} must be an object")
            if 'expected_output' not in test_case:
                raise serializers.ValidationError(
                    f"Test case {i+1} must have 'expected_output' field"
                )
        
        return value


class ActivityCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating activities"""
    
    class Meta:
        model = Activity
        fields = [
            'title', 'description', 'problem_statement', 'starter_code',
            'expected_output', 'test_cases', 'difficulty', 'time_limit',
            'programming_language', 'is_active', 'due_date'
        ]
    
    def validate_test_cases(self, value):
        """Validate that test_cases is a proper list of test case objects"""
        if not isinstance(value, list):
            raise serializers.ValidationError("test_cases must be a list")
        
        for i, test_case in enumerate(value):
            if not isinstance(test_case, dict):
                raise serializers.ValidationError(f"Test case {i+1} must be an object")
            if 'expected_output' not in test_case:
                raise serializers.ValidationError(
                    f"Test case {i+1} must have 'expected_output' field"
                )
        
        return value
