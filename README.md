# Vulnerable Django Notes App (Course Assignment)

This project is an intentionally vulnerable Django web application for cybersecurity coursework.
Do not deploy it in production.

## Features

- User registration and login
- Create, list, view, and delete personal notes
- Search through notes

## Setup

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Run migrations:
   - `python manage.py migrate`
3. Start the app:
   - `python manage.py runserver`
4. Open:
   - `http://127.0.0.1:8000/`

## Flaw/Fix Markers In Code

Each vulnerability is labeled with:
- `# FLAW X: <OWASP category>`

Each corresponding remediation is present as commented code labeled with:
- `# FIX X: <description>`

The fixes are intentionally commented out for assignment demonstration.
