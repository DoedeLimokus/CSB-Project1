from django.db import models


class UserAccount(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password_plaintext = models.CharField(max_length=255)
    password_md5 = models.CharField(max_length=32)

    def __str__(self):
        return self.username


class Note(models.Model):
    owner = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
