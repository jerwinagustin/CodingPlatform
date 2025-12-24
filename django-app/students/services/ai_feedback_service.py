"""
AI Feedback Service for Code Submissions

This service generates educational, tutor-style feedback using Google's Gemini API
after code grading is complete. It provides supportive guidance without revealing solutions.
"""
import logging
from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class AIFeedbackService:
    """
    Service for generating AI-powered educational feedback on code submissions.
    
    Uses Google's Gemini API to provide:
    - Code quality reviews for accepted solutions
    - Educational explanations for wrong answers (without revealing solutions)
    """
    
    # Prompt template for ACCEPTED submissions (code passed all tests)
    PROMPT_TEMPLATE_ACCEPTED = """You are an expert programming tutor. The student got it right. Review this code for cleanliness and efficiency.

**Programming Language:** {language}

**Problem:**
{problem_statement}

**Student's Code:**
```{language}
{source_code}
```

**Instructions:**
Provide constructive feedback on:
1. **Code Quality** - Assess readability, naming conventions, and organization
2. **Efficiency** - Evaluate time/space complexity and suggest optimizations if applicable
3. **Best Practices** - Note any {language}-specific improvements or modern patterns they could adopt
4. **Strengths** - Highlight what they did well

Keep your feedback concise, specific, and actionable. Start with congratulations on getting it right, then provide your review.

**Response:**"""

    # Prompt template for WRONG ANSWER submissions (code failed tests)
    PROMPT_TEMPLATE_WRONG_ANSWER = """You are an expert programming tutor helping a student understand why their code produced incorrect output.

**Context:**
- The student's code has been evaluated and **FAILED one or more test cases**
- Programming Language: {language}
- Problem: {problem_statement}

**Student's Code:**
```{language}
{source_code}
```

**Expected Output (sample):**
```
{expected_output}
```

**Actual Output (student's code produced):**
```
{actual_output}
```
. The student failed. Here is their code, their output, and the error. Explain the logic flaw without revealing the answer.

**Programming Language:** {language}

**Problem:**
{problem_statement}

**Student's Code:**
```{language}
{source_code}
```

**Expected Output:**
```
{expected_output}
```

**Student's Actual Output:**
```
{actual_output}
```

**Instructions:**
1. **Identify the Logic Flaw** - Explain what's wrong with their approach conceptually (without showing the fix)
2. **Analyze the Discrepancy** - Compare expected vs actual output and explain why the difference occurred
3. **Guide Their Thinking** - Ask questions or suggest areas to review that lead them toward understanding
4. **Conceptual Hints** - Point out what they might be misunderstanding about the problem or algorithm

**Critical Rules:**
- Do NOT provide corrected code or direct solutions
- Focus on explaining WHY their logic is flawed
- Help them understand the problem better without giving away the answer

**Your Task:**
Provide comprehensive error analysis covering ALL of the following sections:

## ⚠️ Error Explanation
- Explain what this error message means in simple, beginner-friendly terms
- Describe what type of error this is (syntax, runtime, logic, etc.)
- Explain when and why this error typically occurs

## 📍 Likely Location & Cause
- Point to the specific line(s) or section(s) where the error likely originates
- Explain what in their code triggered this error
- Describe the chain of events that led to this error

## 🔧 How to Debug This
- Walk them through the debugging process step by step
- Suggest specific things to check or verify
- Recommend debugging techniques (print statements, debugger, etc.)
- Ask guiding questions to help them find the fix

## 📚 Understanding This Error Type
- Explain this error category in more depth
- List common causes of this type of error
- Share tips to avoid this error in the future

## 💡 Learning Resources
- Mention related concepts they should understand
- Suggest what to study or practice
- Connect to broader programming principles

**Critical Rules:**
- Do NOT provide the corrected code directly
- Guide them to find the fix themselves
- Be educational and supportive

**Response:**"""

    def __init__(self, api_key: str = None):
        """
        Initialize the AI Feedback service.
        
        Args:
            api_key: Google Gemini API key. Falls back to settings if not provided.
        """
        self.api_key = api_key or getattr(settings, 'GEMINI_API_KEY', None)
        
        # Check if API key is missing or is a placeholder
        if not self.api_key or self.api_key.startswith('YOUR_') or self.api_key == 'YOUR_GEMINI_API_KEY_HERE':
            raise ValueError(
                "Valid Gemini API key is required. "
                "Get your API key from https://aistudio.google.com/app/apikey "
                "and set GEMINI_API_KEY in settings.py"
            )
        
        self.model_name = getattr(settings, 'GEMINI_MODEL_NAME', 'gemini-3-flash-preview')
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Gemini client."""
        try:
            from google import genai
            self.genai_client = genai.Client(api_key=self.api_key)
            self.client = self.genai_client
            logger.info(f"Gemini client initialized with model: {self.model_name}")
        except ImportError:
            # Fallback to old package if new one not installed
            try:
                import google.generativeai as genai_old
                genai_old.configure(api_key=self.api_key)
                self.client = genai_old.GenerativeModel(self.model_name)
                self.genai_client = None
                logger.info(f"Gemini client (legacy) initialized with model: {self.model_name}")
            except ImportError:
                raise ImportError(
                    "google-genai package is required. "
                    "Install it with: pip install google-genai"
                )
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
    
    def build_prompt(
        self,
        verdict: str,
        source_code: str,
        language: str,
        problem_statement: str,
        expected_output: str = "",
        actual_output: str = "",
        error_message: str = ""
    ) -> str:
        """
        Build the appropriate prompt based on the verdict.
        
        Args:
            verdict: 'pass', 'fail', or 'error'
            source_code: The student's submitted code
            language: Programming language used
            problem_statement: The problem description
            expected_output: Expected output (for wrong answers)
            actual_output: Actual output from student's code
            error_message: Error message (for error cases)
        
        Returns:
            Formatted prompt string
        """
        # Truncate outputs if too long (to stay within token limits)
        max_output_length = 10000
        expected_output = self._truncate(expected_output, max_output_length)
        actual_output = self._truncate(actual_output, max_output_length)
        error_message = self._truncate(error_message, max_output_length)
        
        # Truncate source code if extremely long
        max_code_length = 30000
        source_code = self._truncate(source_code, max_code_length)
        
        # Truncate problem statement
        max_problem_length = 10000
        problem_statement = self._truncate(problem_statement, max_problem_length)
        
        if verdict.lower() == 'pass':
            return self.PROMPT_TEMPLATE_ACCEPTED.format(
                language=language,
                problem_statement=problem_statement,
                source_code=source_code
            )
        elif verdict.lower() == 'error':
            return self.PROMPT_TEMPLATE_ERROR.format(
                language=language,
                problem_statement=problem_statement,
                source_code=source_code,
                error_message=error_message
            )
        else:  # fail / wrong answer
            return self.PROMPT_TEMPLATE_WRONG_ANSWER.format(
                language=language,
                problem_statement=problem_statement,
                source_code=source_code,
                expected_output=expected_output,
                actual_output=actual_output
            )
    
    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text with ellipsis if too long."""
        if not text:
            return ""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "\n... [truncated]"
    
    def generate_feedback(
        self,
        verdict: str,
        source_code: str,
        language: str,
        problem_statement: str,
        expected_output: str = "",
        actual_output: str = "",
        error_message: str = "",
        max_tokens: int = 10000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate AI feedback for a code submission.
        
        Args:
            verdict: 'pass', 'fail', or 'error'
            source_code: The student's submitted code
            language: Programming language used
            problem_statement: The problem description
            expected_output: Expected output (for wrong answers)
            actual_output: Actual output from student's code
            error_message: Error message (for error cases)
            max_tokens: Maximum tokens in response
            temperature: Creativity parameter (0-1)
        
        Returns:
            Dictionary with:
                - success: bool
                - feedback: str (the AI-generated feedback)
                - verdict_type: str ('accepted', 'wrong_answer', 'error')
                - error: str (if failed)
        """
        try:
            prompt = self.build_prompt(
                verdict=verdict,
                source_code=source_code,
                language=language,
                problem_statement=problem_statement,
                expected_output=expected_output,
                actual_output=actual_output,
                error_message=error_message
            )
            
            # Determine verdict type for response
            verdict_type = 'accepted' if verdict.lower() == 'pass' else (
                'error' if verdict.lower() == 'error' else 'wrong_answer'
            )
            
            # Generate response from Gemini
            if self.genai_client:
                # New google-genai package
                from google.genai import types
                response = self.genai_client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        max_output_tokens=10000,
                        temperature=temperature,
                    )
                )
                feedback_text = response.text.strip()
            else:
                # Legacy google-generativeai package
                generation_config = {
                    'max_output_tokens': 10000,
                    'temperature': temperature,
                }
                response = self.client.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                feedback_text = response.text.strip()
            
            logger.info(f"Generated AI feedback for verdict: {verdict_type}")
            
            return {
                'success': True,
                'feedback': feedback_text,
                'verdict_type': verdict_type,
                'model_used': self.model_name,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error generating AI feedback: {e}")
            return {
                'success': False,
                'feedback': None,
                'verdict_type': None,
                'model_used': self.model_name,
                'error': str(e)
            }
    
    def generate_feedback_for_submission(self, submission) -> Dict[str, Any]:
        """
        Generate AI feedback for a Submission model instance.
        
        This is a convenience method that extracts all necessary fields
        from the submission object.
        
        Args:
            submission: Submission model instance
        
        Returns:
            Dictionary with feedback result
        """
        # Determine verdict based on result
        if submission.result == 'pass':
            verdict = 'pass'
        elif submission.result == 'error':
            verdict = 'error'
        else:
            verdict = 'fail'
        
        # Get expected output from test results or activity
        expected_output = ""
        actual_output = submission.output or ""
        
        if submission.test_results:
            # Get expected/actual from first failed test case
            for test in submission.test_results:
                if not test.get('passed', False):
                    expected_output = test.get('expected_output', '')
                    actual_output = test.get('actual_output', actual_output)
                    break
            # If all passed, just use first test case
            if not expected_output and submission.test_results:
                expected_output = submission.test_results[0].get('expected_output', '')
                actual_output = submission.test_results[0].get('actual_output', actual_output)
        
        # Fallback to activity's expected output
        if not expected_output and hasattr(submission, 'activity'):
            expected_output = submission.activity.expected_output or ""
        
        return self.generate_feedback(
            verdict=verdict,
            source_code=submission.code,
            language=submission.language,
            problem_statement=submission.activity.problem_statement if hasattr(submission, 'activity') else "",
            expected_output=expected_output,
            actual_output=actual_output,
            error_message=submission.error_message or ""
        )


# Factory function for easy service instantiation
def get_ai_feedback_service(api_key: str = None) -> AIFeedbackService:
    """
    Get an instance of the AI Feedback service.
    
    Args:
        api_key: Optional Gemini API key (uses settings if not provided)
    
    Returns:
        AIFeedbackService instance
    """
    return AIFeedbackService(api_key=api_key)
