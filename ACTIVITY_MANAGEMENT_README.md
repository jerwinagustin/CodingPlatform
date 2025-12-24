# Activity Management Feature - Professor Side

## Overview

Professors can now create, view, edit, and delete coding activities (problems) with expected outputs and test cases. This feature is fully integrated with both the Django backend and React frontend.

## Features Implemented

### Backend (Django)

#### 1. Activity Model (`professors/models.py`)

- **Fields:**
  - `professor` - ForeignKey to Professor who created the activity
  - `title` - Activity title
  - `description` - Brief description
  - `problem_statement` - Detailed problem description
  - `starter_code` - Optional code template for students
  - `expected_output` - Expected output format/example
  - `test_cases` - JSON field containing test case inputs and outputs
  - `difficulty` - Easy, Medium, or Hard
  - `time_limit` - Time limit in minutes
  - `programming_language` - Python, JavaScript, Java, C++, C
  - `is_active` - Whether activity is visible to students
  - `due_date` - Optional due date
  - Timestamps: `created_at`, `updated_at`

#### 2. API Endpoints (`professors/urls.py`)

- `GET /api/professors/activities/` - List all activities for a professor
- `POST /api/professors/activities/create/` - Create a new activity
- `GET /api/professors/activities/<id>/` - Get specific activity details
- `PUT/PATCH /api/professors/activities/<id>/update/` - Update an activity
- `DELETE /api/professors/activities/<id>/delete/` - Delete an activity

#### 3. Security Features

- Activities are linked to the professor who created them
- Professors can only edit/delete their own activities
- Input validation for test cases (must have `input` and `expected_output` fields)

### Frontend (React)

#### 1. ActivityManager Component (`components/ActivityManager.jsx`)

A comprehensive component that provides:

- **Create Mode:** Form to create new activities with all fields
- **Edit Mode:** Edit existing activities
- **List View:** Display all activities in card format
- **Delete:** Remove activities with confirmation

#### 2. Form Features

- Title and difficulty selection
- Rich text areas for description and problem statement
- Code editor for starter code and expected output
- Dynamic test case management (add/remove test cases)
- Programming language selection
- Time limit configuration
- Due date picker
- Active/inactive toggle

#### 3. Activity Display

- Card-based layout showing all activities
- Badge indicators for difficulty level
- Status indicators (Active/Inactive)
- Quick edit and delete actions
- Metadata display (time limit, language, due date)

## Usage Guide

### For Professors:

1. **Login to Professor Dashboard**

   - Navigate to Professor Login
   - Enter credentials

2. **Access Activity Management**

   - Click "Activities" tab in the navigation bar
   - Or click "Manage Activities" in Quick Actions

3. **Create New Activity**

   - Click "+ Create New Activity" button
   - Fill in required fields:
     - Title
     - Description
     - Problem Statement
     - Expected Output
     - At least one test case
   - Optional fields:
     - Starter Code
     - Time Limit (default 60 min)
     - Programming Language (default Python)
     - Due Date
     - Active status

4. **Test Cases**

   - Each test case must have:
     - Input: What will be provided to the student's code
     - Expected Output: What the code should produce
   - Add multiple test cases using "+ Add Test Case"
   - Remove test cases with the "✕" button

5. **Edit Activity**

   - Click "Edit" on any activity card
   - Modify fields as needed
   - Click "Update Activity"

6. **Delete Activity**

   - Click "Delete" on any activity card
   - Confirm deletion in the popup

7. **Toggle Activity Status**
   - Use the "Active" checkbox when creating/editing
   - Active activities are visible to students
   - Inactive activities are hidden

## Data Structure

### Test Case Format (JSON)

```json
[
  {
    "input": "[2, 7, 11, 15], 9",
    "expected_output": "[0, 1]"
  },
  {
    "input": "[3, 2, 4], 6",
    "expected_output": "[1, 2]"
  }
]
```

### Example Activity Payload

```json
{
  "title": "Two Sum Problem",
  "description": "Find two numbers that add up to target",
  "problem_statement": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
  "starter_code": "def two_sum(nums, target):\n    # Your code here\n    pass",
  "expected_output": "[0, 1]",
  "test_cases": [
    {
      "input": "[2,7,11,15], 9",
      "expected_output": "[0,1]"
    }
  ],
  "difficulty": "easy",
  "time_limit": 60,
  "programming_language": "python",
  "is_active": true,
  "due_date": "2025-12-31T23:59:59Z"
}
```

## API Request Examples

### Create Activity

```javascript
POST /api/professors/activities/create/
Headers: Authorization: Bearer <token>
Body: {
  "professor_id": 1,
  "title": "Two Sum",
  "description": "Array problem",
  "problem_statement": "Find two numbers...",
  "expected_output": "[0, 1]",
  "test_cases": [
    {"input": "[2,7,11,15], 9", "expected_output": "[0,1]"}
  ],
  "difficulty": "easy",
  "programming_language": "python"
}
```

### Get Activities

```javascript
GET /api/professors/activities/?professor_id=1
Headers: Authorization: Bearer <token>
```

### Update Activity

```javascript
PUT /api/professors/activities/5/update/
Headers: Authorization: Bearer <token>
Body: {
  "professor_id": 1,
  "title": "Updated Title",
  // ... other fields
}
```

### Delete Activity

```javascript
DELETE /api/professors/activities/5/delete/
Headers: Authorization: Bearer <token>
Body: {
  "professor_id": 1
}
```

## Next Steps (Future Enhancements)

1. **Student Side:**

   - View available activities
   - Submit code solutions
   - Run code against test cases
   - View results and scores

2. **Code Execution:**

   - Integrate code execution engine
   - Run student submissions against test cases
   - Security sandboxing for code execution

3. **Analytics:**

   - Track student submissions
   - Success rates per activity
   - Average completion times

4. **Additional Features:**
   - Activity categories/tags
   - Difficulty-based filtering
   - Search functionality
   - Clone existing activities
   - Import/Export activities

## Files Modified/Created

### Backend:

- `django-app/professors/models.py` - Added Activity model
- `django-app/professors/serializers.py` - Added Activity serializers
- `django-app/professors/views.py` - Added Activity CRUD views
- `django-app/professors/urls.py` - Added Activity endpoints
- `django-app/professors/migrations/0002_activity.py` - Migration file

### Frontend:

- `first-app/src/components/ActivityManager.jsx` - New component
- `first-app/src/components/ActivityManager.css` - Styling
- `first-app/src/pages/ProfessorDashboard.jsx` - Updated with tabs
- `first-app/src/pages/Dashboard.css` - Added tab styles
- `first-app/src/services/api.js` - Added Activity API endpoints

## Testing

To test the feature:

1. Start Django backend:

   ```bash
   cd django-app
   python manage.py runserver
   ```

2. Start React frontend:

   ```bash
   cd first-app
   npm run dev
   ```

3. Login as a professor and navigate to the Activities tab

4. Create a test activity and verify CRUD operations work correctly

## Notes

- All activity operations require professor authentication
- Test cases are validated to ensure they have both input and expected_output
- Activities are automatically associated with the logged-in professor
- The UI is fully responsive and works on mobile devices
