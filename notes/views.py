import hashlib
from functools import wraps

from django.contrib.auth.hashers import check_password, make_password
from django.db import connection
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .models import Note, UserAccount


def get_current_user(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return UserAccount.objects.filter(id=user_id).first()


def login_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not get_current_user(request):
            return redirect("login")
        return view_func(request, *args, **kwargs)

    return wrapped


def register(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        if not username or not password:
            context["error"] = "Username and password are required."
            return render(request, "notes/register.html", context)

        if UserAccount.objects.filter(username=username).exists():
            context["error"] = "Username already exists."
            return render(request, "notes/register.html", context)

        # FLAW 2: A07 - Authentication Failures
        plaintext_password = password
        # FIX 2: Store only a secure password hash and never plaintext passwords
        # plaintext_password = ""
        # secure_hash = make_password(password)

        # FLAW 5: A02 - Cryptographic Failures
        md5_password = hashlib.md5(password.encode("utf-8")).hexdigest()
        # FIX 5: Use Django's strong password hashing instead of MD5
        # md5_password = make_password(password)

        user = UserAccount.objects.create(
            username=username,
            password_plaintext=plaintext_password,
            password_md5=md5_password,
        )
        request.session["user_id"] = user.id
        return redirect("dashboard")
    return render(request, "notes/register.html", context)


def login_view(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = UserAccount.objects.filter(username=username).first()
        if not user:
            context["error"] = "Invalid credentials."
            return render(request, "notes/login.html", context)

        supplied_md5 = hashlib.md5(password.encode("utf-8")).hexdigest()
        # FLAW 2: A07 - Authentication Failures
        # FLAW 5: A02 - Cryptographic Failures
        if user.password_plaintext == password and user.password_md5 == supplied_md5:
            request.session["user_id"] = user.id
            return redirect("dashboard")
        # FIX 2: Verify only secure hashes and remove plaintext dependency
        # FIX 5: Replace MD5 verification with Django password hash checking
        # if check_password(password, user.password_md5):
        #     request.session["user_id"] = user.id
        #     return redirect("dashboard")

        context["error"] = "Invalid credentials."
    return render(request, "notes/login.html", context)


def logout_view(request):
    request.session.flush()
    return redirect("login")


@login_required
def dashboard(request):
    current_user = get_current_user(request)
    context = {"current_user": current_user}

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        if title and content:
            Note.objects.create(owner=current_user, title=title, content=content)
        return redirect("dashboard")

    query = request.GET.get("q", "").strip()
    context["query"] = query

    if query:
        # FLAW 1: A03 - SQL Injection
        raw_sql = (
            "SELECT id, owner_id, title, content, created_at "
            "FROM notes_note "
            f"WHERE owner_id = {current_user.id} "
            f"AND (title LIKE '%{query}%' OR content LIKE '%{query}%') "
            "ORDER BY created_at DESC"
        )
        with connection.cursor() as cursor:
            cursor.execute(raw_sql)
            rows = cursor.fetchall()
        # FIX 1: Use parameterized query (or ORM filtering) to prevent injection
        # raw_sql = (
        #     "SELECT id, owner_id, title, content, created_at "
        #     "FROM notes_note "
        #     "WHERE owner_id = %s AND (title LIKE %s OR content LIKE %s) "
        #     "ORDER BY created_at DESC"
        # )
        # search_value = f"%{query}%"
        # with connection.cursor() as cursor:
        #     cursor.execute(raw_sql, [current_user.id, search_value, search_value])
        #     rows = cursor.fetchall()
        notes = [
            {"id": row[0], "owner_id": row[1], "title": row[2], "content": row[3], "created_at": row[4]}
            for row in rows
        ]
    else:
        notes = Note.objects.filter(owner=current_user).order_by("-created_at")

    context["notes"] = notes
    return render(request, "notes/dashboard.html", context)


@login_required
def note_detail(request, note_id):
    # FLAW 3: A01 - Broken Access Control
    note = get_object_or_404(Note, id=note_id)
    # FIX 3: Enforce ownership check so users can only access their own notes
    # note = get_object_or_404(Note, id=note_id, owner=get_current_user(request))
    return render(request, "notes/note_detail.html", {"note": note, "current_user": get_current_user(request)})


@login_required
def delete_note(request, note_id):
    if request.method != "POST":
        return HttpResponseForbidden("Delete must use POST")
    note = get_object_or_404(Note, id=note_id, owner=get_current_user(request))
    note.delete()
    return redirect("dashboard")
