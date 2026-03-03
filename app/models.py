from django.utils.timezone import now, timedelta
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, BaseUserManager

class Project(models.Model):
    STATUS_CHOICES = [
        ('design', 'Design'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    description = models.TextField()
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    client_name = models.CharField(max_length=64, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="design")
    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(null=True)
    updated = models.DateTimeField(default=timezone.now)
    due = models.DateField(null=True)
    priority = models.CharField(max_length=10, default='medium')

    def get_progress(self):
        """Calculate project completion percentage"""
        tasks = self.task_set.all()
        if not tasks.exists():
            return 0
        completed = tasks.filter(status='COMPLETE').count()
        return (completed / tasks.count()) * 100 if tasks.count() > 0 else 0

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created']

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('urgent', 'Urgent'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

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
    updated = models.DateTimeField(default=timezone.now)
    due = models.DateField(null=True)

    # ClickUp-style features
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    time_estimate = models.IntegerField(null=True, blank=True, help_text="Time estimate in minutes")
    time_logged = models.IntegerField(default=0, help_text="Time spent in minutes")
    dependent_on = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='dependents')
    email_notification_sent = models.BooleanField(default=False)
    completion_notification_sent = models.BooleanField(default=False)


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

class Lead(models.Model):
    id = models.AutoField(primary_key=True)
    client_name = models.CharField(max_length=64)
    client_email = models.EmailField()
    client_contact = models.CharField(max_length=15)
    status = models.CharField(max_length=10, default="ACTIVE")
    notes = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(default=timezone.now)

class IPAddress(models.Model):
    ip = models.GenericIPAddressField(unique=True)  # Store IPv4/IPv6
    request_count = models.IntegerField(default=0)  # Number of requests
    blocked_until = models.DateTimeField(null=True, blank=True)  # Block expiry time

    def is_blocked(self):
        """Check if the IP is currently blocked."""
        return self.blocked_until and self.blocked_until > now()

    def reset_block(self):
        """Reset block status."""
        self.request_count = 0
        self.blocked_until = None
        self.save()

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=[
        ('password_reset', 'Password Reset'),
        ('email_verification', 'Email Verification'),
        ('two_factor_auth', 'Two Factor Authentication')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        """Check if OTP is still valid and not used."""
        return not self.is_used and timezone.now() < self.expires_at

    class Meta:
        ordering = ['-created_at']

class TwoFactorAuth(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='two_factor_auth')
    is_enabled = models.BooleanField(default=False)
    method = models.CharField(max_length=20, choices=[
        ('email_otp', 'Email OTP'),
        ('authenticator', 'Authenticator App')
    ], default='email_otp')
    backup_codes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_backup_codes(self):
        """Get list of backup codes."""
        if self.backup_codes:
            return self.backup_codes.split(',')
        return []

    def use_backup_code(self, code):
        """Use a backup code."""
        codes = self.get_backup_codes()
        if code in codes:
            codes.remove(code)
            self.backup_codes = ','.join(codes)
            self.save()
            return True
        return False


class TaskComment(models.Model):
    """Task comments with @mention support"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    mentions = models.ManyToManyField(User, related_name='mentioned_in_comments', blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username} on {self.task.name}"

    def get_mentions(self):
        """Extract @mentions from content"""
        import re
        pattern = r'@(\w+)'
        matches = re.findall(pattern, self.content)
        return matches


class TaskAttachment(models.Model):
    """File attachments for tasks"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='task_attachments/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)  # image, pdf, document, etc.
    file_size = models.BigIntegerField()  # In bytes
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.filename}"


class ActivityLog(models.Model):
    """Activity log for tasks and projects"""
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('assigned', 'Assigned'),
        ('status_changed', 'Status Changed'),
        ('comment_added', 'Comment Added'),
        ('file_attached', 'File Attached'),
        ('mentioned', 'Mentioned'),
        ('completed', 'Completed'),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='activity_logs')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='activity_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['task', '-created_at']),
            models.Index(fields=['project', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.action} on {self.task.name if self.task else self.project.name}"


class TaskNotification(models.Model):
    """Real-time notifications for users"""
    NOTIFICATION_TYPES = [
        ('task_assigned', 'Task Assigned'),
        ('task_completed', 'Task Completed'),
        ('mentioned', 'Mentioned'),
        ('comment_reply', 'Comment Reply'),
        ('file_shared', 'File Shared'),
        ('task_updated', 'Task Updated'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_notifications')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_sent', null=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
        ]

    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.notification_type} - {self.user.username}"


class TeamCollaborationWatcher(models.Model):
    """Track who is watching/following tasks"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='watchers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watching_tasks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('task', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} watching {self.task.name}"