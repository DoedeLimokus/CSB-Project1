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

## Required OWASP Flaws Included

1. **A03 - SQL Injection**
   - Location: `notes/views.py` (`dashboard` search logic)
   - Behavior: raw SQL is built with direct string interpolation from user input.
   - Example: search for `' OR 1=1 --` to manipulate filtering.

2. **A07 - Authentication Failures**
   - Location: `notes/views.py` (`register`)
   - Behavior: password is stored in plaintext (`password_plaintext`).

3. **A01 - Broken Access Control**
   - Location: `notes/views.py` (`note_detail`)
   - Behavior: note lookup uses only note ID and does not verify owner, enabling IDOR.
   - Example: log in as one user, then manually browse to `/notes/<other_id>/`.

4. **A05 - Security Misconfiguration**
   - Location: `vulnnotes/settings.py`
   - Behavior: `DEBUG = True`, exposing detailed error traces.

5. **A02 - Cryptographic Failures**
   - Location: `notes/views.py` (`register`)
   - Behavior: password is hashed with MD5 (`hashlib.md5`) which is weak and outdated.

## Flaw/Fix Markers In Code

Each vulnerability is labeled with:
- `# FLAW X: <OWASP category>`

Each corresponding remediation is present as commented code labeled with:
- `# FIX X: <description>`

The fixes are intentionally commented out for assignment demonstration.
