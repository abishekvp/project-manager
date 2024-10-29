from django.contrib.auth.models import User, BaseUserManager
from django.db import models

class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    description = models.TextField()
    manager = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
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
            f"Lead: {self.manager.username if self.manager else 'No manager assigned'}\n"
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
    correction = models.TextField(null=True)
    pull_request = models.TextField(null=True)
    reason = models.TextField(null=True)
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

class PersonalTask(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    description = models.TextField()
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=10, default="TODO")
    correction = models.TextField(null=True)
    discussion = models.TextField(null=True)
    reason = models.TextField(null=True)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    permission = models.CharField(max_length=64)
    reason = models.TextField(null=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    access = models.BooleanField(default=False)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=15, blank=True, null=True)
    designation = models.CharField(max_length=64, blank=True, null=True)
    department = models.CharField(max_length=64, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

