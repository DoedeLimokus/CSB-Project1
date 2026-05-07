from django.contrib import admin

from .models import Note, UserAccount

admin.site.register(UserAccount)
admin.site.register(Note)
