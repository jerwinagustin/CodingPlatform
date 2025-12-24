# Django Starter App 🚀

A minimal Django project starter, similar to `npm create vite@latest` but for Django.

## Quick Start

### 1. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create superuser (for admin panel)

```bash
python manage.py createsuperuser
```

### 5. Run development server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

## Project Structure

```
django-app/
├── config/           # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/             # Main app
│   ├── models.py     # Database models
│   ├── views.py      # View functions
│   ├── urls.py       # URL routes
│   └── admin.py      # Admin configuration
├── templates/        # HTML templates
├── static/           # CSS, JS, images
├── manage.py         # Django CLI
└── requirements.txt
```

## Features

✅ Clean, minimal structure  
✅ Pre-configured settings  
✅ Sample Post model with admin  
✅ Basic templates with CSS  
✅ Ready for development

## Next Steps

- Add your models in `core/models.py`
- Create views in `core/views.py`
- Design templates in `templates/`
- Add static files in `static/`
- Configure database in `config/settings.py`

## Commands

| Command                            | Description       |
| ---------------------------------- | ----------------- |
| `python manage.py runserver`       | Start dev server  |
| `python manage.py makemigrations`  | Create migrations |
| `python manage.py migrate`         | Apply migrations  |
| `python manage.py createsuperuser` | Create admin user |
| `python manage.py test`            | Run tests         |

## Admin Panel

Access at: **http://127.0.0.1:8000/admin**

## Production Notes

Before deploying:

- Change `SECRET_KEY` in settings.py
- Set `DEBUG = False`
- Configure `ALLOWED_HOSTS`
- Use PostgreSQL/MySQL instead of SQLite
- Set up static file serving (whitenoise, S3, etc.)
- Add environment variables for sensitive data

## License

MIT
