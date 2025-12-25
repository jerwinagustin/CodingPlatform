# JWT Authentication with MongoDB - Django Backend

## Overview
This Django backend implements JWT authentication for Professors and Students using MongoDB as the database.
## Features

- Separate authentication modules for Professors and Students
- JWT token-based authentication
- MongoDB database integration
- Password hashing and validation
- Registration and login endpoints

## Prerequisites

- Python 3.8+
- MongoDB installed and running on localhost:27017
- MongoDB credentials: username=admin, password=987654321

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run migrations:

```bash
python manage.py migrate
```

3. Create superuser (optional):

```bash
python manage.py createsuperuser
```

4. Run the server:

```bash
python manage.py runserver
```

## API Endpoints

### Professor Authentication

#### Register Professor

- **URL**: `POST /api/professors/register/`
- **Body**:

```json
{
  "employee_id": "PROF001",
  "email": "prof@example.com",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "first_name": "John",
  "last_name": "Doe",
  "department": "Computer Science",
  "phone": "1234567890"
}
```

- **Response**: Returns professor data and JWT tokens (access and refresh)

#### Login Professor

- **URL**: `POST /api/professors/login/`
- **Body**:

```json
{
  "email": "prof@example.com",
  "password": "securepass123"
}
```

- **Response**: Returns professor data and JWT tokens

#### Get Professor Profile

- **URL**: `GET /api/professors/profile/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: Returns professor profile data

### Student Authentication

#### Register Student

- **URL**: `POST /api/students/register/`
- **Body**:

```json
{
  "student_id": "STU001",
  "email": "student@example.com",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "first_name": "Jane",
  "last_name": "Smith",
  "program": "Computer Science",
  "year": 2,
  "phone": "1234567890"
}
```

- **Response**: Returns student data and JWT tokens

#### Login Student

- **URL**: `POST /api/students/login/`
- **Body**:

```json
{
  "email": "student@example.com",
  "password": "securepass123"
}
```

- **Response**: Returns student data and JWT tokens

#### Get Student Profile

- **URL**: `GET /api/students/profile/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: Returns student profile data

## JWT Token Configuration

- **Access Token Lifetime**: 1 hour
- **Refresh Token Lifetime**: 7 days
- **Token Type**: Bearer
- **Algorithm**: HS256

## MongoDB Configuration

The system is configured to connect to MongoDB with the following settings:

- **Host**: localhost:27017
- **Database**: university_db
- **Username**: admin
- **Password**: 987654321
- **Auth Source**: admin

## Models

### Professor Model

- employee_id (unique)
- email (unique)
- password (hashed)
- first_name
- last_name
- department
- phone
- is_active
- created_at
- updated_at

### Student Model

- student_id (unique)
- email (unique)
- password (hashed)
- first_name
- last_name
- program
- year
- phone
- is_active
- created_at
- updated_at

## Security Features

- Passwords are hashed using Django's password hashers
- JWT tokens include user type (professor/student) for role-based access
- Email and ID fields are unique
- Account activation status checking
- Password confirmation validation
- Minimum password length: 8 characters

## Testing with cURL

### Register a Professor:

```bash
curl -X POST http://localhost:8000/api/professors/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "PROF001",
    "email": "prof@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "department": "Computer Science",
    "phone": "1234567890"
  }'
```

### Login as Professor:

```bash
curl -X POST http://localhost:8000/api/professors/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "prof@example.com",
    "password": "password123"
  }'
```

### Testing with Postman

1. Create a new request
2. Set method to POST
3. Enter URL (e.g., http://localhost:8000/api/professors/register/)
4. Go to Headers tab, add: `Content-Type: application/json`
5. Go to Body tab, select "raw" and "JSON", paste the request body
6. Click Send

For authenticated endpoints:

1. Add header: `Authorization: Bearer <your_access_token>`
2. Replace `<your_access_token>` with the token received from login/register
