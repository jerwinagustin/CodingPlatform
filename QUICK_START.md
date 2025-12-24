# Quick Commands Reference

## Start Both Servers

### Option 1: Using PowerShell Script

```powershell
.\start-dev.ps1
```

### Option 2: Manual Start

**Terminal 1 - Django Backend:**

```bash
cd django-app
python manage.py runserver
```

**Terminal 2 - React Frontend:**

```bash
cd first-app
npm run dev
```

---

## Testing the Application

### 1. Open your browser

Navigate to: http://localhost:5173

### 2. Register as a Professor

- Click "Professor" → "Register"
- Fill in the form
- You'll be redirected to the dashboard

### 3. Register as a Student

- Open a new incognito window
- Click "Student" → "Register"
- Fill in the form
- You'll be redirected to the student dashboard

---

## API Endpoints

**Professor:**

- POST /api/professors/register/
- POST /api/professors/login/
- GET /api/professors/profile/

**Student:**

- POST /api/students/register/
- POST /api/students/login/
- GET /api/students/profile/

---

## MongoDB Connection

The system connects to MongoDB with these settings:

- Host: localhost:27017
- Database: university_db
- Username: admin
- Password: 987654321

---

## Troubleshooting

### CORS Error

Make sure:

1. Django is running on port 8000
2. React is running on port 5173
3. django-cors-headers is installed

### MongoDB Connection Error

1. Start MongoDB: `mongod`
2. Check credentials in django-app/config/settings.py

### Port Already in Use

- Django: Change port with `python manage.py runserver 8001`
- React: Change port in vite.config.js or use VITE_PORT=5174

---

## Quick Test Commands

### Test Professor Registration (curl)

```bash
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

### Test Student Login (curl)

```bash
curl -X POST http://localhost:8000/api/students/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@test.com",
    "password": "password123"
  }'
```

---

## Project Structure

```
Just for fun/
├── django-app/          # Django backend
│   ├── professors/      # Professor auth module
│   ├── students/        # Student auth module
│   ├── config/          # Django settings
│   └── manage.py
│
├── first-app/           # React frontend
│   ├── src/
│   │   ├── pages/       # Login, Register, Dashboard pages
│   │   ├── components/  # Reusable components
│   │   ├── context/     # Auth context
│   │   └── services/    # API calls
│   └── package.json
│
└── start-dev.ps1        # Quick start script
```

---

## Next Steps

1. ✅ Backend JWT auth with MongoDB - DONE
2. ✅ Frontend React auth pages - DONE
3. ✅ Integration complete - DONE
4. 🔜 Add more features (courses, assignments, etc.)
