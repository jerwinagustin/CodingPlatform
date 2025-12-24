"""
Celery Tasks for Code Execution

These tasks handle asynchronous code execution and grading via Judge0.
"""
from celery import shared_task
from django.conf import settings
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def _generate_ai_feedback_sync(submission_id: int) -> Dict[str, Any]:
    """
    Synchronous fallback for AI feedback generation when Celery is not available.
    
    This function runs the AI feedback generation synchronously, which is useful
    for development without Redis/Celery running.
    """
    from students.models import Submission
    from students.services import get_ai_feedback_service
    
    try:
        submission = Submission.objects.select_related('activity').get(id=submission_id)
        
        # Only generate feedback for completed submissions
        if submission.status != 'completed':
            return {'success': False, 'error': 'Submission not yet completed'}
        
        # Skip if AI feedback already exists
        if submission.ai_feedback and submission.ai_feedback.get('feedback'):
            return {'success': True, 'already_exists': True}
        
        # Initialize AI feedback service
        try:
            ai_service = get_ai_feedback_service()
        except ValueError as e:
            # Configuration error (missing/invalid API key) - save error for frontend
            error_msg = str(e)
            logger.warning(f"AI service not configured: {error_msg}")
            submission.ai_feedback = {
                'feedback': None,
                'error': error_msg,
                'status': 'error',
                'generated_at': None
            }
            submission.save(update_fields=['ai_feedback', 'updated_at'])
            return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f'AI service initialization failed: {str(e)}'
            logger.error(error_msg)
            submission.ai_feedback = {
                'feedback': None,
                'error': error_msg,
                'status': 'error',
                'generated_at': None
            }
            submission.save(update_fields=['ai_feedback', 'updated_at'])
            return {'success': False, 'error': error_msg}
        
        # Generate feedback
        result = ai_service.generate_feedback_for_submission(submission)
        
        if result['success']:
            submission.ai_feedback = {
                'feedback': result['feedback'],
                'verdict_type': result['verdict_type'],
                'model_used': result['model_used'],
                'generated_at': str(submission.updated_at)
            }
            submission.save(update_fields=['ai_feedback', 'updated_at'])
            logger.info(f"AI feedback generated synchronously for submission {submission_id}")
            return {'success': True, 'feedback': result['feedback']}
        else:
            submission.ai_feedback = {
                'feedback': None,
                'error': result['error'],
                'status': 'error',
                'generated_at': None
            }
            submission.save(update_fields=['ai_feedback', 'updated_at'])
            return {'success': False, 'error': result['error']}
    
    except Submission.DoesNotExist:
        return {'success': False, 'error': 'Submission not found'}
    except Exception as e:
        logger.error(f"Sync AI feedback error: {e}")
        return {'success': False, 'error': str(e)}


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def run_code_task(self, submission_id: int) -> Dict[str, Any]:
    """
    Execute code for a "Run" operation (quick test, no grading).
    
    This task runs the student's code with sample input and returns output.
    It doesn't save to the database - just returns the result.
    
    Args:
        submission_id: ID of the Submission model instance
    
    Returns:
        Dictionary with execution results
    """
    from students.models import Submission
    from students.services import get_judge0_service
    
    try:
        submission = Submission.objects.select_related('activity').get(id=submission_id)
        submission.status = 'running'
        submission.save(update_fields=['status'])
        
        judge0 = get_judge0_service()
        
        # For "Run", we just use the first test case or sample input
        test_cases = submission.activity.test_cases or []
        sample_input = test_cases[0].get('input', '') if test_cases else ''
        
        result = judge0.create_submission(
            source_code=submission.code,
            language=submission.language,
            stdin=sample_input,
            time_limit=5.0,
            wait=True
        )
        
        # Update submission with results
        submission.status = 'completed'
        submission.output = result.get('stdout', '')
        submission.error_message = result.get('stderr') or result.get('compile_output') or result.get('message', '')
        submission.execution_time = float(result.get('time', 0)) if result.get('time') else None
        submission.memory_used = result.get('memory')
        submission.save()
        
        return {
            'submission_id': submission_id,
            'success': result.get('success', False),
            'output': submission.output,
            'error': submission.error_message,
            'time': submission.execution_time,
            'memory': submission.memory_used,
            'status': result.get('status', '')
        }
    
    except Submission.DoesNotExist:
        logger.error(f"Submission {submission_id} not found")
        return {'error': 'Submission not found', 'submission_id': submission_id}
    
    except Exception as e:
        logger.error(f"Error executing code for submission {submission_id}: {e}")
        try:
            submission = Submission.objects.get(id=submission_id)
            submission.status = 'failed'
            submission.error_message = str(e)
            submission.save()
        except:
            pass
        
        # Retry the task
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def submit_code_task(self, submission_id: int) -> Dict[str, Any]:
    """
    Execute code for a "Submit" operation (full grading).
    
    This task runs the student's code against all test cases,
    calculates the score, and saves the results.
    
    Args:
        submission_id: ID of the Submission model instance
    
    Returns:
        Dictionary with grading results
    """
    from students.models import Submission
    from students.services import get_judge0_service
    
    try:
        submission = Submission.objects.select_related('activity').get(id=submission_id)
        submission.status = 'running'
        submission.save(update_fields=['status'])
        
        judge0 = get_judge0_service()
        activity = submission.activity
        
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
            source_code=submission.code,
            language=submission.language,
            test_cases=test_cases,
            time_limit=5.0
        )
        
        # Update submission with grading results
        submission.status = 'completed'
        submission.test_results = grading_result.get('results', [])
        submission.score = grading_result.get('score', 0)
        submission.result = 'pass' if grading_result.get('all_passed', False) else 'fail'
        submission.is_final = True
        
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
        
        # Trigger AI feedback generation asynchronously (non-blocking)
        # This runs after grading is complete and doesn't affect the grade
        try:
            generate_ai_feedback_task.delay(submission_id)
            logger.info(f"Triggered AI feedback generation for submission {submission_id}")
        except Exception as ai_error:
            # Celery/Redis might not be available - try synchronous generation
            logger.warning(f"Celery not available, trying synchronous AI feedback: {ai_error}")
            try:
                _generate_ai_feedback_sync(submission_id)
            except Exception as sync_error:
                logger.warning(f"Synchronous AI feedback also failed: {sync_error}")
        
        return {
            'submission_id': submission_id,
            'success': grading_result.get('all_passed', False),
            'score': submission.score,
            'passed': grading_result.get('passed', 0),
            'total': grading_result.get('total', 0),
            'result': submission.result,
            'test_results': submission.test_results,
            'error': submission.error_message
        }
    
    except Submission.DoesNotExist:
        logger.error(f"Submission {submission_id} not found")
        return {'error': 'Submission not found', 'submission_id': submission_id}
    
    except Exception as e:
        logger.error(f"Error grading submission {submission_id}: {e}")
        try:
            submission = Submission.objects.get(id=submission_id)
            submission.status = 'failed'
            submission.result = 'error'
            submission.error_message = str(e)
            submission.save()
        except:
            pass
        
        # Retry the task
        raise self.retry(exc=e)


@shared_task
def check_submission_status(submission_id: int) -> Dict[str, Any]:
    """
    Check the status of a submission.
    
    Args:
        submission_id: ID of the Submission model instance
    
    Returns:
        Dictionary with current submission status
    """
    from students.models import Submission
    
    try:
        submission = Submission.objects.get(id=submission_id)
        
        return {
            'submission_id': submission_id,
            'status': submission.status,
            'result': submission.result,
            'score': submission.score,
            'output': submission.output,
            'error': submission.error_message,
            'is_complete': submission.status in ['completed', 'failed']
        }
    
    except Submission.DoesNotExist:
        return {'error': 'Submission not found', 'submission_id': submission_id}


@shared_task(bind=True, max_retries=2, default_retry_delay=10)
def generate_ai_feedback_task(self, submission_id: int) -> Dict[str, Any]:
    """
    Generate AI-powered educational feedback for a graded submission.
    
    This task runs AFTER grading is complete. It:
    1. Builds a prompt based on the verdict (pass/fail/error)
    2. Sends the prompt to Gemini API
    3. Saves the feedback to the submission
    
    AI Behavior Rules:
    - For ACCEPTED: Reviews code quality, suggests improvements, does NOT question correctness
    - For WRONG ANSWER: Explains logical mistakes, references output differences, does NOT reveal solution
    - For ERROR: Explains the error message, points to likely cause
    
    Args:
        submission_id: ID of the Submission model instance
    
    Returns:
        Dictionary with AI feedback result
    """
    from students.models import Submission
    from students.services import get_ai_feedback_service
    
    try:
        submission = Submission.objects.select_related('activity').get(id=submission_id)
        
        # Only generate feedback for completed submissions
        if submission.status != 'completed':
            logger.warning(f"Submission {submission_id} not completed, skipping AI feedback")
            return {
                'submission_id': submission_id,
                'success': False,
                'error': 'Submission not yet completed'
            }
        
        # Skip if AI feedback already exists
        if submission.ai_feedback and submission.ai_feedback.get('feedback'):
            logger.info(f"AI feedback already exists for submission {submission_id}")
            return {
                'submission_id': submission_id,
                'success': True,
                'feedback': submission.ai_feedback.get('feedback'),
                'already_exists': True
            }
        
        # Initialize AI feedback service
        try:
            ai_service = get_ai_feedback_service()
        except ValueError as e:
            # Configuration error (missing/invalid API key) - don't retry
            error_msg = str(e)
            logger.error(f"AI service configuration error: {error_msg}")
            
            # Save error to submission so frontend can display it
            submission.ai_feedback = {
                'feedback': None,
                'error': error_msg,
                'status': 'error',
                'generated_at': None
            }
            submission.save(update_fields=['ai_feedback', 'updated_at'])
            
            return {
                'submission_id': submission_id,
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
            
            # Save error to submission
            submission.ai_feedback = {
                'feedback': None,
                'error': f'AI service initialization failed: {str(e)}',
                'status': 'error',
                'generated_at': None
            }
            submission.save(update_fields=['ai_feedback', 'updated_at'])
            
            return {
                'submission_id': submission_id,
                'success': False,
                'error': f'AI service initialization failed: {str(e)}'
            }
        
        # Generate feedback
        result = ai_service.generate_feedback_for_submission(submission)
        
        if result['success']:
            # Save feedback to submission
            submission.ai_feedback = {
                'feedback': result['feedback'],
                'verdict_type': result['verdict_type'],
                'model_used': result['model_used'],
                'generated_at': str(submission.updated_at)
            }
            submission.save(update_fields=['ai_feedback', 'updated_at'])
            
            logger.info(f"AI feedback generated for submission {submission_id}")
            
            return {
                'submission_id': submission_id,
                'success': True,
                'feedback': result['feedback'],
                'verdict_type': result['verdict_type']
            }
        else:
            logger.error(f"AI feedback generation failed: {result['error']}")
            
            # Save error state
            submission.ai_feedback = {
                'feedback': None,
                'error': result['error'],
                'generated_at': None
            }
            submission.save(update_fields=['ai_feedback', 'updated_at'])
            
            # Retry on failure
            raise Exception(result['error'])
    
    except Submission.DoesNotExist:
        logger.error(f"Submission {submission_id} not found")
        return {'error': 'Submission not found', 'submission_id': submission_id}
    
    except Exception as e:
        logger.error(f"Error generating AI feedback for submission {submission_id}: {e}")
        
        # Retry the task
        raise self.retry(exc=e)
