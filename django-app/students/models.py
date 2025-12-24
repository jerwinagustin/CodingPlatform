from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Student(models.Model):
    student_id = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    program = models.CharField(max_length=100)
    year = models.IntegerField()
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'students'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"

    def set_password(self, raw_password):
        """Hash and set the password"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check if the provided password matches"""
        return check_password(raw_password, self.password)


class Submission(models.Model):
    """Model for storing code submissions"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    RESULT_CHOICES = [
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('error', 'Error'),
        ('timeout', 'Timeout'),
        ('pending', 'Pending'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')
    activity = models.ForeignKey('professors.Activity', on_delete=models.CASCADE, related_name='submissions')
    code = models.TextField(help_text="Student's submitted code")
    language = models.CharField(max_length=50, default='python')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='pending')
    score = models.IntegerField(default=0, help_text="Score out of 100")
    test_results = models.JSONField(default=list, help_text="Detailed results for each test case")
    output = models.TextField(blank=True, help_text="Actual output from execution")
    error_message = models.TextField(blank=True, help_text="Error message if any")
    execution_time = models.FloatField(null=True, blank=True, help_text="Execution time in seconds")
    memory_used = models.IntegerField(null=True, blank=True, help_text="Memory used in KB")
    celery_task_id = models.CharField(max_length=100, blank=True, help_text="Celery task ID for tracking")
    is_final = models.BooleanField(default=False, help_text="True for submit, False for run/test")
    
    # AI Feedback field - stores educational feedback generated after grading
    # Schema: {
    #   "feedback": "AI-generated educational feedback text",
    #   "verdict_type": "accepted" | "wrong_answer" | "error",
    #   "model_used": "gemini-1.5-flash",
    #   "generated_at": "2025-12-22T10:30:00Z",
    #   "error": null | "error message if generation failed"
    # }
    ai_feedback = models.JSONField(
        default=dict, 
        blank=True,
        help_text="AI-generated educational feedback after grading"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'submissions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Submission #{self.id} - {self.student} - {self.activity.title}"
    
    @property
    def passed_tests(self):
        """Count of passed test cases"""
        return sum(1 for t in self.test_results if t.get('passed', False))
    
    @property
    def total_tests(self):
        """Total number of test cases"""
        return len(self.test_results)
