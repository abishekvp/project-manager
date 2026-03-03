from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Profile, TwoFactorAuth, Task

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        TwoFactorAuth.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_save, sender=Task)
def send_task_notification_email(sender, instance, created, update_fields, **kwargs):
    """Send email when task is assigned or completed"""
    try:
        # Check if task is assigned and email hasn't been sent yet
        if instance.assigned_to and not instance.email_notification_sent:
            if created or (update_fields and 'assigned_to' in update_fields):
                send_task_assignment_email(instance)

        # Check if task is completed and completion email hasn't been sent
        if instance.status == 'COMPLETE' and not instance.completion_notification_sent:
            if update_fields and 'status' in update_fields:
                send_task_completion_email(instance)
    except Exception as e:
        print(f"Error sending email notification: {str(e)}")

def send_task_assignment_email(task):
    """Send email to assigned user when task is assigned"""
    try:
        if not task.assigned_to or not task.assigned_to.email:
            return

        context = {
            'user_name': task.assigned_to.first_name or task.assigned_to.username,
            'task_name': task.name,
            'project_name': task.project.name,
            'task_description': task.description,
            'due_date': task.due,
            'priority': task.get_priority_display(),
            'assigned_by': task.project.manager.get_full_name() or task.project.manager.username if task.project.manager else 'System',
            'task_url': f'{settings.SITE_URL}/task-detail/?id={task.id}' if hasattr(settings, 'SITE_URL') else '#'
        }

        html_message = render_to_string('emails/task_assignment.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=f'New Task Assigned: {task.name}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[task.assigned_to.email],
            html_message=html_message,
            fail_silently=True,
        )

        task.email_notification_sent = True
        Task.objects.filter(id=task.id).update(email_notification_sent=True)
    except Exception as e:
        print(f"Error sending assignment email: {str(e)}")

def send_task_completion_email(task):
    """Send email when task is completed"""
    try:
        recipients = []

        # Send to assigned user
        if task.assigned_to and task.assigned_to.email:
            recipients.append(task.assigned_to.email)

        # Send to project manager
        if task.project.manager and task.project.manager.email:
            recipients.append(task.project.manager.email)

        if not recipients:
            return

        context = {
            'task_name': task.name,
            'project_name': task.project.name,
            'completed_by': task.assigned_to.get_full_name() or task.assigned_to.username if task.assigned_to else 'Unknown',
            'completion_date': task.updated,
            'task_url': f'{settings.SITE_URL}/task-detail/?id={task.id}' if hasattr(settings, 'SITE_URL') else '#'
        }

        html_message = render_to_string('emails/task_completion.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=f'Task Completed: {task.name}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=list(set(recipients)),  # Remove duplicates
            html_message=html_message,
            fail_silently=True,
        )

        task.completion_notification_sent = True
        Task.objects.filter(id=task.id).update(completion_notification_sent=True)
    except Exception as e:
        print(f"Error sending completion email: {str(e)}")