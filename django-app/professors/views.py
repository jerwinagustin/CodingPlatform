from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import IntegrityError
from .models import Professor, Activity
from .serializers import (
    ProfessorRegistrationSerializer,
    ProfessorLoginSerializer,
    ProfessorSerializer,
    ActivitySerializer,
    ActivityCreateUpdateSerializer
)


def get_tokens_for_professor(professor):
    """Generate JWT tokens for professor"""
    refresh = RefreshToken()
    refresh['professor_id'] = professor.id
    refresh['email'] = professor.email
    refresh['user_type'] = 'professor'
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def professor_register(request):
    """
    Register a new professor
    POST /api/professors/register/
    Body: {
        "employee_id": "PROF001",
        "email": "prof@example.com",
        "password": "password123",
        "password_confirm": "password123",
        "first_name": "John",
        "last_name": "Doe",
        "department": "Computer Science",
        "phone": "1234567890"
    }
    """
    serializer = ProfessorRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            professor = serializer.save()
            tokens = get_tokens_for_professor(professor)
            
            return Response({
                'message': 'Professor registered successfully',
                'professor': ProfessorSerializer(professor).data,
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)
        
        except IntegrityError as e:
            return Response({
                'error': 'Professor with this email or employee ID already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def professor_login(request):
    """
    Login professor
    POST /api/professors/login/
    Body: {
        "email": "prof@example.com",
        "password": "password123"
    }
    """
    serializer = ProfessorLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            professor = Professor.objects.get(email=email)
            
            if not professor.is_active:
                return Response({
                    'error': 'This account has been deactivated'
                }, status=status.HTTP_403_FORBIDDEN)
            
            if professor.check_password(password):
                tokens = get_tokens_for_professor(professor)
                
                return Response({
                    'message': 'Login successful',
                    'professor': ProfessorSerializer(professor).data,
                    'tokens': tokens
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        except Professor.DoesNotExist:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def professor_profile(request):
    """
    Get professor profile (requires authentication)
    GET /api/professors/profile/
    Headers: Authorization: Bearer <access_token>
    """
    # In a real implementation, you'd extract professor_id from JWT token
    # For now, this is a placeholder that requires proper JWT middleware
    professor_id = request.user.id if hasattr(request.user, 'id') else None
    
    if not professor_id:
        return Response({
            'error': 'Authentication required'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        professor = Professor.objects.get(id=professor_id)
        return Response(ProfessorSerializer(professor).data)
    except Professor.DoesNotExist:
        return Response({
            'error': 'Professor not found'
        }, status=status.HTTP_404_NOT_FOUND)


# Activity Management Views

@api_view(['POST'])
@permission_classes([AllowAny])
def create_activity(request):
    """
    Create a new activity (coding problem)
    POST /api/professors/activities/
    Headers: Authorization: Bearer <access_token>
    Body: {
        "title": "Two Sum Problem",
        "description": "Find two numbers that add up to target",
        "problem_statement": "Given an array of integers...",
        "starter_code": "def two_sum(nums, target):\n    pass",
        "expected_output": "[0, 1]",
        "test_cases": [
            {"input": "[2,7,11,15], 9", "expected_output": "[0,1]"},
            {"input": "[3,2,4], 6", "expected_output": "[1,2]"}
        ],
        "difficulty": "easy",
        "time_limit": 60,
        "programming_language": "python",
        "is_active": true,
        "due_date": "2025-12-31T23:59:59Z"
    }
    """
    # Extract professor_id from JWT token
    professor_id = request.data.get('professor_id')
    
    if not professor_id:
        return Response({
            'error': 'Professor ID is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        professor = Professor.objects.get(id=professor_id)
    except Professor.DoesNotExist:
        return Response({
            'error': 'Professor not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ActivityCreateUpdateSerializer(data=request.data)
    
    if serializer.is_valid():
        activity = serializer.save(professor=professor)
        return Response({
            'message': 'Activity created successfully',
            'activity': ActivitySerializer(activity).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_activities(request):
    """
    List all activities for a professor
    GET /api/professors/activities/?professor_id=1
    Headers: Authorization: Bearer <access_token>
    """
    professor_id = request.query_params.get('professor_id')
    
    if not professor_id:
        return Response({
            'error': 'Professor ID is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        professor = Professor.objects.get(id=professor_id)
        activities = Activity.objects.filter(professor=professor)
        serializer = ActivitySerializer(activities, many=True)
        
        return Response({
            'count': activities.count(),
            'activities': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Professor.DoesNotExist:
        return Response({
            'error': 'Professor not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_activity(request, activity_id):
    """
    Get a specific activity by ID
    GET /api/professors/activities/{activity_id}/
    Headers: Authorization: Bearer <access_token>
    """
    try:
        activity = Activity.objects.get(id=activity_id)
        serializer = ActivitySerializer(activity)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Activity.DoesNotExist:
        return Response({
            'error': 'Activity not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT', 'PATCH'])
@permission_classes([AllowAny])
def update_activity(request, activity_id):
    """
    Update an activity
    PUT/PATCH /api/professors/activities/{activity_id}/
    Headers: Authorization: Bearer <access_token>
    """
    try:
        activity = Activity.objects.get(id=activity_id)
    except Activity.DoesNotExist:
        return Response({
            'error': 'Activity not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Verify professor owns this activity
    professor_id = request.data.get('professor_id')
    if str(activity.professor.id) != str(professor_id):
        return Response({
            'error': 'You do not have permission to update this activity'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ActivityCreateUpdateSerializer(
        activity, 
        data=request.data, 
        partial=(request.method == 'PATCH')
    )
    
    if serializer.is_valid():
        activity = serializer.save()
        return Response({
            'message': 'Activity updated successfully',
            'activity': ActivitySerializer(activity).data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_activity(request, activity_id):
    """
    Delete an activity
    DELETE /api/professors/activities/{activity_id}/
    Headers: Authorization: Bearer <access_token>
    """
    try:
        activity = Activity.objects.get(id=activity_id)
    except Activity.DoesNotExist:
        return Response({
            'error': 'Activity not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Verify professor owns this activity
    professor_id = request.data.get('professor_id') or request.query_params.get('professor_id')
    if str(activity.professor.id) != str(professor_id):
        return Response({
            'error': 'You do not have permission to delete this activity'
        }, status=status.HTTP_403_FORBIDDEN)
    
    activity.delete()
    return Response({
        'message': 'Activity deleted successfully'
    }, status=status.HTTP_200_OK)
