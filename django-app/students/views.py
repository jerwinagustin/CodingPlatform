from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import IntegrityError
from .models import Student, Submission
from .serializers import (
    StudentRegistrationSerializer,
    StudentLoginSerializer,
    StudentSerializer,
    CodeRunSerializer,
    CodeSubmitSerializer,
    SubmissionSerializer
)
from professors.models import Activity
from professors.serializers import ActivitySerializer
from .services import get_judge0_service
from .tasks import run_code_task, submit_code_task


def get_tokens_for_student(student):
    """Generate JWT tokens for student"""
    refresh = RefreshToken()
    refresh['student_id'] = student.id
    refresh['email'] = student.email
    refresh['user_type'] = 'student'
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def student_register(request):
    """
    Register a new student
    POST /api/students/register/
    Body: {
        "student_id": "STU001",
        "email": "student@example.com",
        "password": "password123",
        "password_confirm": "password123",
        "first_name": "Jane",
        "last_name": "Smith",
        "program": "Computer Science",
        "year": 2,
        "phone": "1234567890"
    }
    """
    serializer = StudentRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            student = serializer.save()
            tokens = get_tokens_for_student(student)
            
            return Response({
                'message': 'Student registered successfully',
                'student': StudentSerializer(student).data,
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)
        
        except IntegrityError as e:
            return Response({
                'error': 'Student with this email or student ID already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def student_login(request):
    """
    Login student
    POST /api/students/login/
    Body: {
        "email": "student@example.com",
        "password": "password123"
    }
    """
    serializer = StudentLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            student = Student.objects.get(email=email)
            
            if not student.is_active:
                return Response({
                    'error': 'This account has been deactivated'
                }, status=status.HTTP_403_FORBIDDEN)
            
            if student.check_password(password):
                tokens = get_tokens_for_student(student)
                
                return Response({
                    'message': 'Login successful',
                    'student': StudentSerializer(student).data,
                    'tokens': tokens
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        except Student.DoesNotExist:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def student_profile(request):
    """
    Get student profile (requires authentication)
    GET /api/students/profile/
    Headers: Authorization: Bearer <access_token>
    """
    # In a real implementation, you'd extract student_id from JWT token
    # For now, this is a placeholder that requires proper JWT middleware
    student_id = request.user.id if hasattr(request.user, 'id') else None
    
    if not student_id:
        return Response({
            'error': 'Authentication required'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        student = Student.objects.get(id=student_id)
        return Response(StudentSerializer(student).data)
    except Student.DoesNotExist:
        return Response({
            'error': 'Student not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])  # For now, allow any - in production, use proper JWT auth
def get_student_activities(request):
    """
    Get all active activities for students to view
    GET /api/students/activities/
    """
    # Get all active activities ordered by most recent first
    activities = Activity.objects.filter(is_active=True).select_related('professor').order_by('-created_at')
    
    serializer = ActivitySerializer(activities, many=True)
    
    return Response({
        'count': activities.count(),
        'activities': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_activity_detail(request, activity_id):
    """
    Get a specific activity for students to work on
    GET /api/students/activities/<activity_id>/
    """
    try:
        activity = Activity.objects.select_related('professor').get(id=activity_id, is_active=True)
        serializer = ActivitySerializer(activity)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Activity.DoesNotExist:
        return Response({
            'error': 'Activity not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])  # For now - should require JWT auth in production
def run_code(request):
    """
    Run code for quick testing (no grading, no saving)
    
    POST /api/students/code/run/
    Body: {
        "activity_id": 1,
        "code": "print('Hello')",
        "language": "python",
        "input": "optional input"
    }
    
    This is the "Run" button - quick test against sample input.
    Flow: React → Django → Judge0 → React (skips Celery for speed)
    """
    serializer = CodeRunSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    activity_id = serializer.validated_data['activity_id']
    code = serializer.validated_data['code']
    language = serializer.validated_data['language']
    custom_input = serializer.validated_data.get('input', '')
    
    try:
        activity = Activity.objects.get(id=activity_id, is_active=True)
    except Activity.DoesNotExist:
        return Response({
            'error': 'Activity not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        judge0 = get_judge0_service()
        
        # Use custom input or first test case input
        if not custom_input and activity.test_cases:
            custom_input = activity.test_cases[0].get('input', '')
        
        # Execute code directly (synchronous for quick feedback)
        result = judge0.create_submission(
            source_code=code,
            language=language,
            stdin=custom_input,
            time_limit=5.0,
            wait=True
        )
        
        return Response({
            'success': result.get('success', False),
            'output': result.get('stdout', ''),
            'error': result.get('stderr') or result.get('compile_output') or result.get('message', ''),
            'time': result.get('time'),
            'memory': result.get('memory'),
            'status': result.get('status', ''),
            'input_used': custom_input
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])  # For now - should require JWT auth in production
def submit_code(request):
    """
    Submit code for grading (runs against all test cases)
    
    POST /api/students/code/submit/
    Body: {
        "activity_id": 1,
        "student_id": 1,
        "code": "def solution(): ...",
        "language": "python"
    }
    
    This is the "Submit" button - full grading.
    Flow: React → Django → Celery → Judge0 → Celery → React
    """
    serializer = CodeSubmitSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    activity_id = serializer.validated_data['activity_id']
    code = serializer.validated_data['code']
    language = serializer.validated_data['language']
    student_id = request.data.get('student_id')
    
    if not student_id:
        return Response({
            'error': 'student_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        activity = Activity.objects.get(id=activity_id, is_active=True)
    except Activity.DoesNotExist:
        return Response({
            'error': 'Activity not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response({
            'error': 'Student not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Create submission record
    submission = Submission.objects.create(
        student=student,
        activity=activity,
        code=code,
        language=language,
        status='pending',
        is_final=True
    )
    
    # Queue the grading task with Celery
    task = submit_code_task.delay(submission.id)
    submission.celery_task_id = task.id
    submission.save(update_fields=['celery_task_id'])
    
    return Response({
        'message': 'Code submitted for grading',
        'submission_id': submission.id,
        'task_id': task.id,
        'status': 'pending'
    }, status=status.HTTP_202_ACCEPTED)


@api_view(['POST'])
@permission_classes([AllowAny])  # For now - should require JWT auth in production
def submit_code_sync(request):
    """
    Submit code for grading (synchronous - waits for result)
    
    POST /api/students/code/submit-sync/
    Body: {
        "activity_id": 1,
        "student_id": 1,
        "code": "def solution(): ...",
        "language": "python"
    }
    
    This is an alternative "Submit" button that waits for the result.
    Use this if Celery/Redis is not running.
    """
    serializer = CodeSubmitSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    activity_id = serializer.validated_data['activity_id']
    code = serializer.validated_data['code']
    language = serializer.validated_data['language']
    student_id = request.data.get('student_id')
    
    if not student_id:
        return Response({
            'error': 'student_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        activity = Activity.objects.get(id=activity_id, is_active=True)
    except Activity.DoesNotExist:
        return Response({
            'error': 'Activity not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response({
            'error': 'Student not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Create submission record
    submission = Submission.objects.create(
        student=student,
        activity=activity,
        code=code,
        language=language,
        status='running',
        is_final=True
    )
    
    try:
        judge0 = get_judge0_service()
        
        # Get test cases from the activity
        test_cases = activity.test_cases or []
        
        if not test_cases:
            # If no test cases defined, use the expected_output field
            test_cases = [{
                'input': '',
                'expected_output': activity.expected_output
            }]
        
        # Run all test cases
        grading_result = judge0.run_test_cases(
            source_code=code,
            language=language,
            test_cases=test_cases,
            time_limit=5.0
        )
        
        # Update submission with grading results
        submission.status = 'completed'
        submission.test_results = grading_result.get('results', [])
        submission.score = grading_result.get('score', 0)
        submission.result = 'pass' if grading_result.get('all_passed', False) else 'fail'
        
        # Collect any errors from test results
        errors = []
        for test_result in submission.test_results:
            if test_result.get('error'):
                errors.append(f"Test {test_result.get('test_case', '?')}: {test_result['error']}")
        
        submission.error_message = '\n'.join(errors) if errors else ''
        
        # Get the first output as main output
        if submission.test_results:
            submission.output = submission.test_results[0].get('actual_output', '')
        
        submission.save()
        
        # Trigger AI feedback generation (sync fallback since we're not using Celery)
        from students.tasks import _generate_ai_feedback_sync
        try:
            _generate_ai_feedback_sync(submission.id)
        except Exception as ai_error:
            # AI feedback is optional - don't fail the grading if AI fails
            import logging
            logging.getLogger(__name__).warning(f"AI feedback generation failed: {ai_error}")
        
        return Response({
            'submission_id': submission.id,
            'success': grading_result.get('all_passed', False),
            'score': submission.score,
            'passed': grading_result.get('passed', 0),
            'total': grading_result.get('total', 0),
            'result': submission.result,
            'test_results': submission.test_results,
            'error': submission.error_message
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        submission.status = 'failed'
        submission.result = 'error'
        submission.error_message = str(e)
        submission.save()
        
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_submission_status(request, submission_id):
    """
    Get the status of a submission
    
    GET /api/students/submissions/<submission_id>/status/
    
    Use this to poll for submission results when using async submit.
    """
    try:
        submission = Submission.objects.get(id=submission_id)
        
        return Response({
            'submission_id': submission.id,
            'status': submission.status,
            'result': submission.result,
            'score': submission.score,
            'output': submission.output,
            'error': submission.error_message,
            'test_results': submission.test_results,
            'passed_tests': submission.passed_tests,
            'total_tests': submission.total_tests,
            'is_complete': submission.status in ['completed', 'failed']
        }, status=status.HTTP_200_OK)
    
    except Submission.DoesNotExist:
        return Response({
            'error': 'Submission not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_student_submissions(request):
    """
    Get all submissions for a student
    
    GET /api/students/submissions/?student_id=1&activity_id=1
    """
    student_id = request.query_params.get('student_id')
    activity_id = request.query_params.get('activity_id')
    
    if not student_id:
        return Response({
            'error': 'student_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    submissions = Submission.objects.filter(student_id=student_id, is_final=True)
    
    if activity_id:
        submissions = submissions.filter(activity_id=activity_id)
    
    submissions = submissions.select_related('activity', 'student').order_by('-created_at')
    
    serializer = SubmissionSerializer(submissions, many=True)
    
    return Response({
        'count': submissions.count(),
        'submissions': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_ai_feedback(request, submission_id):
    """
    Get AI-generated feedback for a submission
    
    GET /api/students/submissions/<submission_id>/ai-feedback/
    
    Returns the AI feedback if available, or status indicating it's still generating.
    Can optionally trigger generation if not yet started.
    """
    try:
        submission = Submission.objects.get(id=submission_id)
        
        ai_feedback = submission.ai_feedback or {}
        
        # Check if feedback exists
        if ai_feedback.get('feedback'):
            return Response({
                'submission_id': submission.id,
                'has_feedback': True,
                'feedback': ai_feedback.get('feedback'),
                'verdict_type': ai_feedback.get('verdict_type'),
                'model_used': ai_feedback.get('model_used'),
                'generated_at': ai_feedback.get('generated_at'),
            }, status=status.HTTP_200_OK)
        
        # Check if there was an error generating feedback
        if ai_feedback.get('error'):
            return Response({
                'submission_id': submission.id,
                'has_feedback': False,
                'status': 'error',
                'error': ai_feedback.get('error'),
            }, status=status.HTTP_200_OK)
        
        # Feedback not yet available - check if we should trigger it
        if submission.status == 'completed' and not ai_feedback:
            # Trigger AI feedback generation if not already started
            from students.tasks import generate_ai_feedback_task, _generate_ai_feedback_sync
            try:
                generate_ai_feedback_task.delay(submission_id)
            except Exception:
                # Celery not available - try synchronous generation
                try:
                    _generate_ai_feedback_sync(submission_id)
                    # Reload submission to get updated ai_feedback
                    submission.refresh_from_db()
                    ai_feedback = submission.ai_feedback or {}
                    
                    if ai_feedback.get('feedback'):
                        return Response({
                            'submission_id': submission.id,
                            'has_feedback': True,
                            'feedback': ai_feedback.get('feedback'),
                            'verdict_type': ai_feedback.get('verdict_type'),
                            'model_used': ai_feedback.get('model_used'),
                            'generated_at': ai_feedback.get('generated_at'),
                        }, status=status.HTTP_200_OK)
                    
                    if ai_feedback.get('error'):
                        return Response({
                            'submission_id': submission.id,
                            'has_feedback': False,
                            'status': 'error',
                            'error': ai_feedback.get('error'),
                        }, status=status.HTTP_200_OK)
                except Exception:
                    pass  # Silently fail - AI feedback is optional
        
        return Response({
            'submission_id': submission.id,
            'has_feedback': False,
            'status': 'generating',
            'message': 'AI feedback is being generated. Please try again in a few seconds.',
        }, status=status.HTTP_200_OK)
    
    except Submission.DoesNotExist:
        return Response({
            'error': 'Submission not found'
        }, status=status.HTTP_404_NOT_FOUND)
