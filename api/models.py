from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Messages(models.Model):
    name = models.CharField(max_length=32)
    email = models.EmailField()
    message = models.TextField()
    contact = models.CharField(max_length=16)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

class TokenUser(models.Model):
    token = models.CharField(max_length=64, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)