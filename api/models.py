from django.db import models

# Create your models here.
class Messages(models.Model):
    name = models.CharField(max_length=32)
    email = models.EmailField()
    message = models.TextField()
    contact = models.CharField(max_length=16)