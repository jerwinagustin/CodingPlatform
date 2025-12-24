# AI Feedback System for Code Judge

This document describes the AI-powered educational feedback system integrated into the code judge platform. The system generates supportive, tutor-style feedback after code grading is complete.

## Overview

The AI feedback system uses **Google's Gemini API** to generate educational feedback for student submissions. It runs asynchronously after grading completes and provides:

- **For Accepted submissions**: Code quality reviews, efficiency suggestions, best practices
- **For Wrong Answer submissions**: Conceptual explanations without revealing solutions
- **For Error submissions**: Error message explanations and debugging hints

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  submit_code_   │────▶│  Grading via     │────▶│  generate_ai_   │
│  task (Celery)  │     │  Judge0          │     │  feedback_task  │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │  Gemini API     │
                                                 │  (LLM)          │
                                                 └────────┬────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │  MongoDB/SQLite │
                                                 │  (ai_feedback)  │
                                                 └─────────────────┘
```

## Files Structure

```
students/
├── services/
│   ├── __init__.py
│   ├── judge0_service.py      # Existing code execution
│   └── ai_feedback_service.py # NEW: AI feedback generation
├── models.py                  # Updated: ai_feedback field
├── tasks.py                   # Updated: generate_ai_feedback_task
└── ...

config/
└── settings.py                # Updated: GEMINI_API_KEY, GEMINI_MODEL_NAME
```

## Setup

### 1. Install Dependencies

```bash
pip install google-generativeai>=0.8.0
```

Or update all requirements:

```bash
pip install -r requirements.txt
```

### 2. Get Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Add to `config/settings.py`:

```python
GEMINI_API_KEY = 'your-actual-api-key-here'
GEMINI_MODEL_NAME = 'gemini-1.5-flash'  # or 'gemini-1.5-pro' for better quality
```

### 3. Run Database Migration

```bash
python manage.py makemigrations students
python manage.py migrate
```

### 4. Start Celery Worker

The AI feedback task runs via Celery (you already have this set up):

```bash
celery -A config worker -l info
```

## MongoDB Schema

The `ai_feedback` field is stored as a JSON document embedded in each submission:

```json
{
  "ai_feedback": {
    "feedback": "Your solution correctly computes the factorial...",
    "verdict_type": "accepted",
    "model_used": "gemini-1.5-flash",
    "generated_at": "2025-12-22T10:30:00Z",
    "error": null
  }
}
```

### Schema Definition

| Field          | Type        | Description                                        |
| -------------- | ----------- | -------------------------------------------------- |
| `feedback`     | string      | The AI-generated educational feedback text         |
| `verdict_type` | string      | `"accepted"`, `"wrong_answer"`, or `"error"`       |
| `model_used`   | string      | The Gemini model used (e.g., `"gemini-1.5-flash"`) |
| `generated_at` | string      | ISO timestamp when feedback was generated          |
| `error`        | string/null | Error message if generation failed, otherwise null |

## Prompt Templates

### For ACCEPTED Submissions (Passed All Tests)

````
You are a supportive programming tutor reviewing a student's code submission.

**Context:**
- The student's code has been evaluated and **PASSED all test cases**
- Programming Language: {language}
- Problem: {problem_statement}

**Student's Code:**
```{language}
{source_code}
````

**Your Task:**
Since the code is CORRECT, do NOT question its correctness. Instead:

1. Briefly acknowledge that the solution works correctly
2. Review the code quality, structure, and readability
3. Suggest 1-2 small improvements for:
   - Code efficiency or performance
   - Naming conventions or code style
   - Best practices for this language
   - Edge case handling (if applicable)

**Tone Guidelines:**

- Be supportive and encouraging
- Keep feedback concise (1-2 short paragraphs)
- Focus on growth, not criticism
- Do NOT rewrite or provide alternative solutions

```

### For WRONG ANSWER Submissions (Failed Tests)

```

You are a supportive programming tutor helping a student understand why their code produced incorrect output.

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

**Your Task:**
Help the student understand their mistake WITHOUT giving away the solution:

1. Identify the likely logical error or misconception
2. Explain WHY the output differs from expected (reference specific differences)
3. Give a hint about the direction to investigate
4. Encourage them to trace through their logic

**Critical Rules:**

- Do NOT provide the correct solution or fixed code
- Do NOT write any code corrections
- Focus on conceptual understanding
- Be supportive and non-judgmental

````

## Example Feedback Outputs

### Example 1: Accepted Submission (Factorial Problem)

**Student Code:**
```python
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)
````

**AI Feedback:**

> Your solution correctly computes the factorial using recursion — nice work! The base case is properly handled, and the recursive logic is clean and easy to follow.
>
> One thing to consider: for very large values of `n`, this recursive approach might hit Python's recursion limit. If you're working with larger numbers, you could explore an iterative approach using a loop, which would be more memory-efficient.

### Example 2: Wrong Answer (Two Sum Problem)

**Student Code:**

```python
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
```

**Expected Output:** `[0, 1]`
**Actual Output:** `[0, 0]`

**AI Feedback:**

> I see your code is finding pairs that sum to the target, but the output suggests it might be matching an element with itself. Notice how your actual output `[0, 0]` has the same index twice.
>
> Think about this: when checking pairs, should an element ever be paired with itself? Consider what condition might prevent that from happening. Try tracing through your nested loops with a simple example like `[3, 3]` and target `6` — when does `i` equal `j`?

### Example 3: Error Submission (Syntax Error)

**Student Code:**

```python
def greet(name)
    print(f"Hello, {name}")
```

**Error Message:**

```
SyntaxError: expected ':'
```

**AI Feedback:**

> The error message "expected ':'" is pointing to a missing character in your function definition. In Python, every function definition line must end with a specific punctuation mark before the indented body begins.
>
> Take a look at the line `def greet(name)` — compare it with other function definitions you've written. What character typically appears after the closing parenthesis?

## API Usage

### Manual Feedback Generation

You can manually trigger AI feedback for a submission:

```python
from students.tasks import generate_ai_feedback_task

# Trigger asynchronously
generate_ai_feedback_task.delay(submission_id=123)

# Or run synchronously (for testing)
result = generate_ai_feedback_task(submission_id=123)
print(result['feedback'])
```

### Accessing Feedback in Views

```python
from students.models import Submission

submission = Submission.objects.get(id=123)

# Check if feedback exists
if submission.ai_feedback and submission.ai_feedback.get('feedback'):
    feedback_text = submission.ai_feedback['feedback']
    verdict_type = submission.ai_feedback['verdict_type']
    print(f"[{verdict_type}] {feedback_text}")
else:
    print("No AI feedback available yet")
```

### REST API Response

When returning submission data in your API, include the feedback:

```python
# In your serializer or view
return {
    'submission_id': submission.id,
    'status': submission.status,
    'result': submission.result,
    'score': submission.score,
    'test_results': submission.test_results,
    'ai_feedback': submission.ai_feedback  # Include this field
}
```

## Configuration Options

| Setting             | Default            | Description                                           |
| ------------------- | ------------------ | ----------------------------------------------------- |
| `GEMINI_API_KEY`    | Required           | Your Google Gemini API key                            |
| `GEMINI_MODEL_NAME` | `gemini-1.5-flash` | Model to use (`gemini-1.5-flash` or `gemini-1.5-pro`) |

### Model Comparison

| Model              | Speed   | Quality | Cost   |
| ------------------ | ------- | ------- | ------ |
| `gemini-1.5-flash` | ⚡ Fast | Good    | Lower  |
| `gemini-1.5-pro`   | Slower  | Better  | Higher |

For educational feedback, `gemini-1.5-flash` is recommended as it provides good quality at lower latency and cost.

## Error Handling

The AI feedback system is designed to be **non-blocking**:

- If Gemini API fails, grading still completes successfully
- Failed feedback generation is logged but doesn't affect scores
- The task retries up to 2 times with 10-second delays
- Error state is stored in `ai_feedback.error` for debugging

## Security Considerations

1. **API Key Protection**: Store `GEMINI_API_KEY` in environment variables for production
2. **Content Truncation**: Long code/outputs are truncated to prevent token limit issues
3. **No Solution Leakage**: Prompts explicitly instruct AI not to reveal solutions
4. **Rate Limiting**: Gemini API has rate limits; consider caching for repeated submissions

## Troubleshooting

### "Gemini API key is required"

Ensure `GEMINI_API_KEY` is set in `config/settings.py` or environment variables.

### "google-generativeai package is required"

Install the package:

```bash
pip install google-generativeai
```

### Feedback not appearing

1. Check Celery worker is running
2. Check submission status is `completed`
3. Check logs for errors: `tail -f celery.log`

### Slow feedback generation

- Switch to `gemini-1.5-flash` model
- Reduce `max_tokens` parameter (default: 500)
- Check network latency to Google API

## Future Enhancements

- [ ] Support for multiple LLM providers (OpenAI, Anthropic, local models)
- [ ] Feedback quality rating system
- [ ] Caching for similar submissions
- [ ] Batch feedback generation
- [ ] Language-specific prompt tuning
