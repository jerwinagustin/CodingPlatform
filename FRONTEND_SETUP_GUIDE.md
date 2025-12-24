# Frontend Setup Guide - University Management System

## 🚀 Complete React + Django Integration

### Prerequisites

- Node.js 16+ and npm installed
- Python 3.8+ installed
- MongoDB running on localhost:27017

## Backend Setup (Django)

### 1. Install Python Dependencies

```bash
cd django-app
pip install -r requirements.txt
```

The backend now includes:

- Django REST Framework
- Simple JWT for authentication
- Django CORS Headers (configured for React)
- Djongo for MongoDB integration

### 2. Run Django Server

```bash
python manage.py migrate
python manage.py runserver
```

The Django backend will run on `http://localhost:8000`

**CORS is configured to allow requests from:**

- `http://localhost:5173` (Vite default port)
- `http://127.0.0.1:5173`

---

## Frontend Setup (React)

### 1. Install Node Dependencies

```bash
cd first-app
npm install
```

This installs:

- React 19.2.0
- React Router DOM 7.1.1 (for routing)
- Axios 1.7.9 (for API calls)

### 2. Run React Development Server

```bash
npm run dev
```

The React app will run on `http://localhost:5173`

---

## 📁 Project Structure

### React Frontend Structure

```
first-app/
├── src/
│   ├── components/
│   │   └── ProtectedRoute.jsx        # Route guard for authenticated pages
│   ├── context/
│   │   └── AuthContext.jsx           # Global auth state management
│   ├── pages/
│   │   ├── Home.jsx                  # Landing page with role selection
│   │   ├── Home.css
│   │   ├── ProfessorLogin.jsx        # Professor login form
│   │   ├── ProfessorRegister.jsx     # Professor registration form
│   │   ├── ProfessorDashboard.jsx    # Professor dashboard
│   │   ├── StudentLogin.jsx          # Student login form
│   │   ├── StudentRegister.jsx       # Student registration form
│   │   ├── StudentDashboard.jsx      # Student dashboard
│   │   ├── Auth.css                  # Auth pages styling
│   │   └── Dashboard.css             # Dashboard styling
│   ├── services/
│   │   ├── api.js                    # Axios instance with interceptors
│   │   └── authService.js            # Authentication API functions
│   ├── App.jsx                       # Main app with routing
│   ├── App.css
│   ├── main.jsx                      # React entry point
│   └── index.css
```

### Django Backend Structure

```
django-app/
├── professors/                        # Professor authentication module
│   ├── models.py                     # Professor model
│   ├── serializers.py                # API serializers
│   ├── views.py                      # Registration/Login endpoints
│   ├── urls.py                       # Professor routes
│   └── admin.py                      # Admin interface
├── students/                         # Student authentication module
│   ├── models.py                     # Student model
│   ├── serializers.py                # API serializers
│   ├── views.py                      # Registration/Login endpoints
│   ├── urls.py                       # Student routes
│   └── admin.py                      # Admin interface
└── config/
    ├── settings.py                   # JWT, CORS, MongoDB config
    └── urls.py                       # Main URL routing
```

---

## 🔐 Features Implemented

### Authentication System

- ✅ Separate login/register for Professors and Students
- ✅ JWT token-based authentication
- ✅ Token storage in localStorage
- ✅ Automatic token injection in API requests
- ✅ Protected routes (dashboard pages)
- ✅ Password hashing and validation
- ✅ Form validation on both frontend and backend

### React Features

- ✅ Context API for global auth state
- ✅ React Router for navigation
- ✅ Protected routes with role-based access
- ✅ Axios interceptors for auth headers
- ✅ Beautiful, responsive UI with gradient designs
- ✅ Error handling and loading states
- ✅ Modern CSS styling

### Django Features

- ✅ MongoDB integration via Djongo
- ✅ Separate models for Professors and Students
- ✅ JWT token generation with custom claims
- ✅ CORS configuration for React
- ✅ RESTful API endpoints
- ✅ Password hashing with Django's hashers

---

## 🌐 Available Routes

### Frontend Routes

**Public Routes:**

- `/` - Home page (role selection)
- `/professor/login` - Professor login
- `/professor/register` - Professor registration
- `/student/login` - Student login
- `/student/register` - Student registration

**Protected Routes (require authentication):**

- `/professor/dashboard` - Professor dashboard (professors only)
- `/student/dashboard` - Student dashboard (students only)

### Backend API Endpoints

**Professor Endpoints:**

- `POST /api/professors/register/` - Register new professor
- `POST /api/professors/login/` - Professor login
- `GET /api/professors/profile/` - Get professor profile (auth required)

**Student Endpoints:**

- `POST /api/students/register/` - Register new student
- `POST /api/students/login/` - Student login
- `GET /api/students/profile/` - Get student profile (auth required)

---

## 📝 Usage Examples

### Register a Professor

1. Navigate to `http://localhost:5173`
2. Click "Professor" → "Register"
3. Fill in the form:
   - Employee ID: `PROF001`
   - Email: `prof@university.edu`
   - Password: `password123`
   - First/Last Name, Department, etc.
4. Click "Register"
5. Automatically redirected to Professor Dashboard

### Login as Student

1. Navigate to `http://localhost:5173`
2. Click "Student" → "Login"
3. Enter email and password
4. Click "Login"
5. Redirected to Student Dashboard

### API Call Example (from browser console)

```javascript
// After logging in, try:
const token = localStorage.getItem("accessToken");
console.log("Token:", token);

const userData = localStorage.getItem("userData");
console.log("User:", JSON.parse(userData));
```

---

## 🎨 UI Features

- **Modern Gradient Design**: Purple/blue gradient backgrounds
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Card-based UI**: Clean, modern card layouts
- **Form Validation**: Real-time validation with error messages
- **Loading States**: Visual feedback during API calls
- **Protected Routes**: Automatic redirect if not authenticated
- **Role-based Access**: Professors can't access student dashboard and vice versa

---

## 🔧 Configuration Details

### CORS Settings (Django)

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]
CORS_ALLOW_CREDENTIALS = True
```

### JWT Settings (Django)

- Access Token Lifetime: 1 hour
- Refresh Token Lifetime: 7 days
- Token Type: Bearer
- Algorithm: HS256

### API Base URL (React)

```javascript
// src/services/api.js
const API_BASE_URL = "http://localhost:8000/api";
```

---

## 🧪 Testing the Integration

### Test Professor Registration

```bash
# Using curl
curl -X POST http://localhost:8000/api/professors/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "PROF001",
    "email": "prof@test.com",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "department": "Computer Science",
    "phone": "1234567890"
  }'
```

### Test Student Login

```bash
curl -X POST http://localhost:8000/api/students/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@test.com",
    "password": "password123"
  }'
```

---

## 🐛 Troubleshooting

### CORS Errors

- Make sure Django server is running on port 8000
- Make sure React dev server is running on port 5173
- Check that `django-cors-headers` is installed
- Verify CORS settings in Django `settings.py`

### MongoDB Connection Issues

- Ensure MongoDB is running: `mongod`
- Check credentials in `settings.py`
- Verify database name: `university_db`
- Confirm password: `987654321`

### JWT Token Issues

- Check browser localStorage for tokens
- Verify token format: `Bearer <token>`
- Check token expiration (1 hour default)
- Look for auth errors in browser console

### API Connection Issues

- Verify backend is running on `http://localhost:8000`
- Verify frontend is running on `http://localhost:5173`
- Check browser Network tab for API calls
- Look for CORS headers in response

---

## 🚀 Next Steps

You now have a complete, integrated authentication system! Here's what you can build next:

1. **Course Management**: Add courses, enroll students
2. **Assignment System**: Professors create, students submit
3. **Grading System**: Grade tracking and analytics
4. **Profile Management**: Edit user profiles
5. **File Upload**: Upload documents, assignments
6. **Real-time Features**: WebSocket for notifications
7. **Email Verification**: Verify email on registration
8. **Password Reset**: Forgot password functionality

---

## 📚 Technology Stack

**Frontend:**

- React 19.2.0
- React Router DOM 7.1.1
- Axios 1.7.9
- Vite 7.2.4

**Backend:**

- Django 5.0+
- Django REST Framework 3.14+
- Simple JWT 5.3+
- Djongo 1.3.6
- PyMongo 3.12+

**Database:**

- MongoDB

---

## 💡 Key Files to Modify

### To change API URL:

- Edit `first-app/src/services/api.js`

### To modify auth flow:

- Edit `first-app/src/context/AuthContext.jsx`

### To customize styling:

- Edit CSS files in `first-app/src/pages/`

### To add new API endpoints:

- Add views in `django-app/professors/views.py` or `students/views.py`
- Update URLs in respective `urls.py` files

---

**🎉 Your authentication system is now fully integrated and ready to use!**
