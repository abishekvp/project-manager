from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    description = models.TextField()
    lead = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    client_name = models.CharField(max_length=64)
    status = models.CharField(max_length=10, default="DESIGN")
    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(null=True)
    updated = models.DateTimeField(auto_now=True)
    due = models.DateField(null=True)

    def __str__(self):
        return (
            f"Project: {self.name}\n"
            f"Description: {self.description}\n"
            f"Lead: {self.lead.username if self.lead else 'No lead assigned'}\n"
            f"Client: {self.client_name}\n"
            f"Status: {self.status}\n"
            f"Start Date: {self.started.strftime('%Y-%m-%d')}\n"
            f"Created At: {self.created.strftime('%Y-%m-%d %H:%M')}"
            f"Updated: {self.updated.strftime('%Y-%m-%d %H:%M')}"
            f"Due Date: {self.due.strftime('%Y-%m-%d')}\n"
        )

class Task(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=10, default="TODO")
    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(null=True)
    updated = models.DateTimeField(auto_now=True)
    due = models.DateField(null=True)

    def __str__(self):
        return (
            f"Task: {self.name}\n"
            f"Created: {self.created.strftime('%Y-%m-%d %H:%M')}\n"
            f"Started: {self.started.strftime('%Y-%m-%d %H:%M') if self.started else 'Not started'}\n"
            f"Updated: {self.updated.strftime('%Y-%m-%d %H:%M')}\n"
            f"Due Date: {self.due.strftime('%Y-%m-%d') if self.due else 'No due date'}"
        )

class Assignment(models.Model):
    id = models.AutoField(primary_key=True)
    peer = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

class MailServer(models.Model):
    id = models.AutoField(primary_key=True)
    server = models.CharField(max_length=64)
    port = models.IntegerField()
    username = models.CharField(max_length=64)
    password = models.CharField(max_length=64)
    from_email = models.EmailField()

class Permisison(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.CharField(max_length=64)
    granted = models.BooleanField(default=False)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=15, blank=True, null=True)
