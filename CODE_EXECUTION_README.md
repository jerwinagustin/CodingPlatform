# Code Execution System Documentation

This document explains the code execution system that allows students to take activities with a Monaco code editor, run their code against test cases, and submit for grading.

## Architecture Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    React    │────▶│   Django    │────▶│   Celery    │────▶│   Judge0    │
│  (Frontend) │◀────│  (Backend)  │◀────│  (Tasks)    │◀────│   (API)     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │    Redis    │
                    │  (Broker)   │
                    └─────────────┘
```

## Two Workflows

### 1. "Run" Button (Quick Testing)

**Purpose**: Let students check if their code works against a sample input.

**Flow**: React → Django → Judge0 → React (synchronous, skips Celery)

```
Student clicks "Run"
       │
       ▼
React sends POST /api/students/code/run/
       │
       ▼
Django directly calls Judge0 API
       │
       ▼
Judge0 executes code
       │
       ▼
Django returns output to React
       │
       ▼
React displays output
```

### 2. "Submit" Button (Full Grading)

**Purpose**: Final submission with grading against all test cases.

**Flow**: React → Django → Celery → Judge0 → Celery → Database → React

```
Student clicks "Submit"
       │
       ▼
React sends POST /api/students/code/submit-sync/
       │
       ▼
Django creates Submission record
       │
       ▼
Django calls Judge0 for each test case
       │
       ▼
Judge0 returns results
       │
       ▼
Django calculates score (PASS/FAIL)
       │
       ▼
Django saves results to database
       │
       ▼
React displays results with score
```

## Setup Instructions

### Backend Setup

1. **Install Python dependencies**:

   ```bash
   cd django-app
   pip install -r requirements.txt
   ```

2. **Install and Start Redis** (for Celery):

   **Windows**: Download from https://github.com/microsoftarchive/redis/releases

   ```bash
   redis-server
   ```

   **Linux/Mac**:

   ```bash
   sudo apt-get install redis-server
   redis-server
   ```

3. **Run migrations**:

   ```bash
   python manage.py migrate
   ```

4. **Start Django server**:

   ```bash
   python manage.py runserver
   ```

5. **Start Celery worker** (optional, for async submissions):
   ```bash
   celery -A config worker --loglevel=info --pool=solo
   ```

### Frontend Setup

1. **Install dependencies**:

   ```bash
   cd first-app
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

## API Endpoints

### Run Code (Quick Test)

```
POST /api/students/code/run/
{
    "activity_id": 1,
    "code": "print('Hello')",
    "language": "python",
    "input": "optional custom input"
}

Response:
{
    "success": true,
    "output": "Hello",
    "error": "",
    "time": "0.02",
    "memory": 1024,
    "status": "Accepted"
}
```

### Submit Code (Synchronous Grading)

```
POST /api/students/code/submit-sync/
{
    "activity_id": 1,
    "student_id": 1,
    "code": "x = int(input())\nprint(x * 2)",
    "language": "python"
}

Response:
{
    "submission_id": 1,
    "success": true,
    "score": 100,
    "passed": 3,
    "total": 3,
    "result": "pass",
    "test_results": [
        {
            "test_case": 1,
            "passed": true,
            "input": "5",
            "expected_output": "10",
            "actual_output": "10"
        }
    ]
}
```

### Submit Code (Async with Celery)

```
POST /api/students/code/submit/
{
    "activity_id": 1,
    "student_id": 1,
    "code": "...",
    "language": "python"
}

Response:
{
    "message": "Code submitted for grading",
    "submission_id": 1,
    "task_id": "abc123",
    "status": "pending"
}
```

### Check Submission Status

```
GET /api/students/submissions/{submission_id}/status/

Response:
{
    "submission_id": 1,
    "status": "completed",
    "result": "pass",
    "score": 100,
    "output": "10",
    "error": "",
    "test_results": [...],
    "passed_tests": 3,
    "total_tests": 3,
    "is_complete": true
}
```

## Supported Languages

| Language   | Judge0 ID | Monaco ID  |
| ---------- | --------- | ---------- |
| Python 3   | 71        | python     |
| JavaScript | 63        | javascript |
| Java       | 62        | java       |
| C++        | 54        | cpp        |
| C          | 50        | c          |
| C#         | 51        | csharp     |
| Go         | 60        | go         |
| Ruby       | 72        | ruby       |
| Rust       | 73        | rust       |
| TypeScript | 74        | typescript |
| PHP        | 68        | php        |
| Swift      | 83        | swift      |
| Kotlin     | 78        | kotlin     |

## Activity Test Cases Format

When creating activities, test cases should be in this format:

```json
{
  "test_cases": [
    {
      "input": "5\n3",
      "expected_output": "8"
    },
    {
      "input": "10\n20",
      "expected_output": "30"
    }
  ]
}
```

## Judge0 API

The system uses Judge0 CE (Community Edition) via RapidAPI.

- **API Key**: Configured in `settings.py` as `JUDGE0_API_KEY`
- **Rate Limits**: Check your RapidAPI plan
- **Timeout**: 5 seconds per execution by default

## Database Models

### Submission Model

```python
class Submission:
    student: ForeignKey(Student)
    activity: ForeignKey(Activity)
    code: TextField
    language: CharField
    status: ['pending', 'running', 'completed', 'failed']
    result: ['pass', 'fail', 'error', 'timeout', 'pending']
    score: IntegerField (0-100)
    test_results: JSONField
    output: TextField
    error_message: TextField
    execution_time: FloatField
    memory_used: IntegerField
    is_final: BooleanField
```

## Troubleshooting

### "Connection refused" for Redis

- Make sure Redis server is running
- Check if it's on the correct port (6379)

### Judge0 API Errors

- Verify your API key is correct
- Check RapidAPI rate limits
- Ensure the code isn't timing out (5s limit)

### Code execution hangs

- Check if the code has an infinite loop
- Verify input format matches what code expects
- Check Judge0 API status

## Security Notes

1. **API Key Protection**: The Judge0 API key should be moved to environment variables in production
2. **Authentication**: Currently using AllowAny for testing - implement proper JWT auth
3. **Rate Limiting**: Implement rate limiting to prevent API abuse
4. **Code Sandboxing**: Judge0 handles sandboxing, but validate inputs

## Future Improvements

- [ ] Add WebSocket for real-time submission status updates
- [ ] Implement code plagiarism detection
- [ ] Add more language support
- [ ] Implement submission history view
- [ ] Add code auto-save feature
- [ ] Implement activity timer/countdown
