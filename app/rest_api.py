"""
REST API Views for real-time features:
- Notifications management
- Task comments and mentions
- File attachments
- Activity feed
- Team collaboration
- Dashboard widgets and analytics
"""
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Q, Count, F
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
import os
from .models import (
    Task, Project, TaskComment, TaskAttachment, ActivityLog,
    TaskNotification, TeamCollaborationWatcher
)
from django.contrib.auth.models import User


# ============================================================================
# NOTIFICATIONS API
# ============================================================================

@login_required
@require_http_methods(["GET"])
def api_get_notifications(request):
    """Get user's notifications with pagination and filtering."""
    try:
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        unread_only = request.GET.get('unread_only', 'false').lower() == 'true'

        query = TaskNotification.objects.filter(user=request.user)

        if unread_only:
            query = query.filter(is_read=False)

        total = query.count()
        offset = (page - 1) * per_page
        notifications = query[offset:offset + per_page]

        notif_data = []
        for notif in notifications:
            notif_data.append({
                'id': notif.id,
                'type': notif.notification_type,
                'title': notif.title,
                'message': notif.message,
                'actor': notif.actor.username if notif.actor else None,
                'task_id': notif.task_id,
                'project_id': notif.project_id,
                'is_read': notif.is_read,
                'created_at': notif.created_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'notifications': notif_data,
            'total': total,
            'total_pages': (total + per_page - 1) // per_page,
            'current_page': page
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_mark_notification_read(request):
    """Mark notification as read."""
    try:
        data = json.loads(request.body)
        notification_id = data.get('notification_id')

        notif = get_object_or_404(TaskNotification, id=notification_id, user=request.user)
        notif.mark_as_read()

        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_mark_all_notifications_read(request):
    """Mark all notifications as read."""
    try:
        notifications = TaskNotification.objects.filter(
            user=request.user,
            is_read=False
        )

        for notif in notifications:
            notif.mark_as_read()

        return JsonResponse({
            'success': True,
            'message': f'Marked {notifications.count()} notifications as read'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def api_get_unread_notification_count(request):
    """Get count of unread notifications."""
    try:
        count = TaskNotification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        return JsonResponse({
            'success': True,
            'count': count
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ============================================================================
# TASK COMMENTS API
# ============================================================================

@login_required
@require_http_methods(["GET"])
def api_get_task_comments(request, task_id):
    """Get all comments for a task."""
    try:
        task = get_object_or_404(Task, id=task_id)

        # Authorization check
        if task.assigned_to != request.user and task.project.manager != request.user:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

        comments = TaskComment.objects.filter(task=task).select_related('author')

        comments_data = []
        for comment in comments:
            mentions = [u.username for u in comment.mentions.all()]
            comments_data.append({
                'id': comment.id,
                'author': comment.author.username,
                'author_id': comment.author.id,
                'content': comment.content,
                'created_at': comment.created_at.isoformat(),
                'updated_at': comment.updated_at.isoformat(),
                'mentions': mentions
            })

        return JsonResponse({
            'success': True,
            'comments': comments_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_create_task_comment(request, task_id):
    """Create a new comment on a task."""
    try:
        task = get_object_or_404(Task, id=task_id)

        # Authorization check
        if task.assigned_to != request.user and task.project.manager != request.user:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

        data = json.loads(request.body)
        content = data.get('content', '').strip()

        if not content:
            return JsonResponse({'success': False, 'error': 'Comment cannot be empty'}, status=400)

        comment = TaskComment.objects.create(
            task=task,
            author=request.user,
            content=content
        )

        # Extract and add mentions
        mentions = extract_mentions(content)
        mentioned_users = []

        for username in mentions:
            try:
                user = User.objects.get(username=username)
                comment.mentions.add(user)
                mentioned_users.append(user)

                # Create notification for mentioned user
                TaskNotification.objects.create(
                    user=user,
                    task=task,
                    notification_type='mentioned',
                    title=f'{request.user.username} mentioned you',
                    message=f'{request.user.username} mentioned you in a comment on: {task.name}',
                    actor=request.user
                )

                # Send WebSocket notification
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'notifications_user_{user.id}',
                    {
                        'type': 'notification_created',
                        'notification': {
                            'id': TaskNotification.objects.filter(user=user).latest('created_at').id,
                            'type': 'mentioned',
                            'title': f'{request.user.username} mentioned you',
                            'message': f'{request.user.username} mentioned you in a comment on: {task.name}',
                        },
                        'timestamp': timezone.now().isoformat()
                    }
                )
            except User.DoesNotExist:
                pass

        # Broadcast comment via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'task_comments_{task_id}',
            {
                'type': 'comment_created',
                'comment': {
                    'id': comment.id,
                    'author': comment.author.username,
                    'author_id': comment.author.id,
                    'content': comment.content,
                    'timestamp': comment.created_at.isoformat(),
                    'mentions': [u.username for u in mentioned_users]
                }
            }
        )

        # Log activity
        ActivityLog.objects.create(
            task=task,
            user=request.user,
            action='comment_added',
            description=f'Added comment: {content[:100]}...',
        )

        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'author': comment.author.username,
                'author_id': comment.author.id,
                'content': comment.content,
                'created_at': comment.created_at.isoformat(),
                'mentions': [u.username for u in mentioned_users]
            },
            'message': 'Comment created successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_delete_task_comment(request, comment_id):
    """Delete a task comment (only comment author or task manager can delete)."""
    try:
        comment = get_object_or_404(TaskComment, id=comment_id)

        # Authorization check
        is_author = comment.author == request.user
        is_manager = comment.task.project.manager == request.user

        if not (is_author or is_manager):
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

        task_id = comment.task.id
        comment.delete()

        return JsonResponse({
            'success': True,
            'message': 'Comment deleted successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ============================================================================
# FILE ATTACHMENTS API
# ============================================================================

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
                      'txt', 'zip', 'jpg', 'jpeg', 'png', 'gif', 'bmp'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@login_required
@require_http_methods(["POST"])
def api_upload_task_attachment(request, task_id):
    """Upload a file attachment to a task."""
    try:
        task = get_object_or_404(Task, id=task_id)

        # Authorization check
        if task.assigned_to != request.user and task.project.manager != request.user:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

        if 'file' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No file provided'}, status=400)

        uploaded_file = request.FILES['file']

        # Validate file
        if uploaded_file.size > MAX_FILE_SIZE:
            return JsonResponse({
                'success': False,
                'error': 'File size exceeds 50MB limit'
            }, status=400)

        file_ext = uploaded_file.name.split('.')[-1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            return JsonResponse({
                'success': False,
                'error': f'File type {file_ext} not allowed'
            }, status=400)

        # Determine file type
        file_type = get_file_type(file_ext)

        # Save attachment
        attachment = TaskAttachment.objects.create(
            task=task,
            uploaded_by=request.user,
            file=uploaded_file,
            filename=uploaded_file.name,
            file_type=file_type,
            file_size=uploaded_file.size
        )

        # Log activity
        ActivityLog.objects.create(
            task=task,
            user=request.user,
            action='file_attached',
            description=f'Attached file: {uploaded_file.name}',
        )

        # Notify watchers via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'task_comments_{task_id}',
            {
                'type': 'activity_update',
                'activity': {
                    'type': 'file_attached',
                    'filename': uploaded_file.name,
                    'user': request.user.username
                },
                'timestamp': timezone.now().isoformat()
            }
        )

        return JsonResponse({
            'success': True,
            'attachment': {
                'id': attachment.id,
                'filename': attachment.filename,
                'file_type': attachment.file_type,
                'file_size': attachment.file_size,
                'uploaded_by': attachment.uploaded_by.username,
                'created_at': attachment.created_at.isoformat(),
            },
            'message': 'File uploaded successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def api_get_task_attachments(request, task_id):
    """Get all attachments for a task."""
    try:
        task = get_object_or_404(Task, id=task_id)

        # Authorization check
        if task.assigned_to != request.user and task.project.manager != request.user:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

        attachments = TaskAttachment.objects.filter(task=task)

        attachments_data = []
        for att in attachments:
            attachments_data.append({
                'id': att.id,
                'filename': att.filename,
                'file_type': att.file_type,
                'file_size': att.file_size,
                'uploaded_by': att.uploaded_by.username,
                'created_at': att.created_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'attachments': attachments_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def api_download_attachment(request, attachment_id):
    """Download a file attachment."""
    try:
        attachment = get_object_or_404(TaskAttachment, id=attachment_id)

        # Authorization check
        task = attachment.task
        if task.assigned_to != request.user and task.project.manager != request.user:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

        if attachment.file and default_storage.exists(attachment.file.name):
            file_content = default_storage.open(attachment.file.name, 'rb')
            response = FileResponse(file_content, as_attachment=True, filename=attachment.filename)
            return response

        return JsonResponse({'success': False, 'error': 'File not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_delete_attachment(request, attachment_id):
    """Delete a file attachment."""
    try:
        attachment = get_object_or_404(TaskAttachment, id=attachment_id)

        # Authorization check
        task = attachment.task
        is_uploader = attachment.uploaded_by == request.user
        is_manager = task.project.manager == request.user

        if not (is_uploader or is_manager):
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

        filename = attachment.filename

        # Delete file from storage
        if attachment.file and default_storage.exists(attachment.file.name):
            default_storage.delete(attachment.file.name)

        attachment.delete()

        return JsonResponse({
            'success': True,
            'message': f'Attachment {filename} deleted'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ============================================================================
# ACTIVITY FEED API
# ============================================================================

@login_required
@require_http_methods(["GET"])
def api_get_activity_feed(request):
    """Get activity feed for user's tasks and projects."""
    try:
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        task_id = request.GET.get('task_id')
        project_id = request.GET.get('project_id')

        query = ActivityLog.objects.select_related('user', 'task', 'project')

        if task_id:
            query = query.filter(task_id=task_id)
        elif project_id:
            query = query.filter(project_id=project_id)
        else:
            # Get activities for user's tasks and managed projects
            query = query.filter(
                Q(task__assigned_to=request.user) |
                Q(task__project__manager=request.user) |
                Q(project__manager=request.user)
            ).distinct()

        total = query.count()
        offset = (page - 1) * per_page
        activities = query.order_by('-created_at')[offset:offset + per_page]

        activities_data = []
        for activity in activities:
            activities_data.append({
                'id': activity.id,
                'user': activity.user.username,
                'action': activity.action,
                'description': activity.description,
                'task_id': activity.task_id,
                'task_name': activity.task.name if activity.task else None,
                'project_id': activity.project_id,
                'project_name': activity.project.name if activity.project else None,
                'old_value': activity.old_value,
                'new_value': activity.new_value,
                'created_at': activity.created_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'activities': activities_data,
            'total': total,
            'total_pages': (total + per_page - 1) // per_page,
            'current_page': page
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ============================================================================
# TEAM COLLABORATION API
# ============================================================================

@login_required
@require_http_methods(["POST"])
def api_watch_task(request, task_id):
    """Add user as watcher to a task."""
    try:
        task = get_object_or_404(Task, id=task_id)

        watcher, created = TeamCollaborationWatcher.objects.get_or_create(
            task=task,
            user=request.user
        )

        return JsonResponse({
            'success': True,
            'message': 'Now watching task',
            'is_watching': True
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_unwatch_task(request, task_id):
    """Remove user as watcher from a task."""
    try:
        task = get_object_or_404(Task, id=task_id)

        TeamCollaborationWatcher.objects.filter(
            task=task,
            user=request.user
        ).delete()

        return JsonResponse({
            'success': True,
            'message': 'Stopped watching task',
            'is_watching': False
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def api_get_task_watchers(request, task_id):
    """Get list of users watching a task."""
    try:
        task = get_object_or_404(Task, id=task_id)

        watchers = TeamCollaborationWatcher.objects.filter(task=task).select_related('user')

        watchers_data = []
        for watcher in watchers:
            watchers_data.append({
                'id': watcher.user.id,
                'username': watcher.user.username,
                'email': watcher.user.email,
            })

        # Check if current user is watching
        is_watching = TeamCollaborationWatcher.objects.filter(
            task=task,
            user=request.user
        ).exists()

        return JsonResponse({
            'success': True,
            'watchers': watchers_data,
            'watcher_count': len(watchers_data),
            'is_watching': is_watching
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ============================================================================
# DASHBOARD WIDGETS & ANALYTICS API
# ============================================================================

@login_required
@require_http_methods(["GET"])
def api_get_dashboard_analytics(request):
    """Get comprehensive dashboard analytics."""
    try:
        user = request.user

        # Task statistics
        my_tasks = Task.objects.filter(assigned_to=user)
        my_projects = Project.objects.filter(manager=user)

        task_by_priority = {
            'urgent': my_tasks.filter(priority='urgent').count(),
            'high': my_tasks.filter(priority='high').count(),
            'medium': my_tasks.filter(priority='medium').count(),
            'low': my_tasks.filter(priority='low').count(),
        }

        task_by_status = {
            'TODO': my_tasks.filter(status='TODO').count(),
            'IN_PROGRESS': my_tasks.filter(status='IN_PROGRESS').count(),
            'REVIEW': my_tasks.filter(status='REVIEW').count(),
            'COMPLETE': my_tasks.filter(status='COMPLETE').count(),
        }

        # Time tracking
        total_time_estimated = sum([t.time_estimate or 0 for t in my_tasks])
        total_time_logged = sum([t.time_logged or 0 for t in my_tasks])

        # Project statistics
        project_stats = []
        for project in my_projects[:10]:
            total = project.task_set.count()
            completed = project.task_set.filter(status='COMPLETE').count()
            progress = (completed / total * 100) if total > 0 else 0

            project_stats.append({
                'name': project.name,
                'total_tasks': total,
                'completed_tasks': completed,
                'progress': int(progress)
            })

        # Recent activity
        recent_activities = ActivityLog.objects.filter(
            Q(task__assigned_to=user) |
            Q(project__manager=user)
        ).select_related('user', 'task', 'project')[:5]

        activities = []
        for activity in recent_activities:
            activities.append({
                'user': activity.user.username,
                'action': activity.action,
                'description': activity.description,
                'timestamp': activity.created_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'analytics': {
                'tasks': {
                    'total': my_tasks.count(),
                    'completed': my_tasks.filter(status='COMPLETE').count(),
                    'in_progress': my_tasks.filter(status='IN_PROGRESS').count(),
                    'overdue': my_tasks.filter(
                        due__lt=timezone.now().date(),
                        status__in=['TODO', 'IN_PROGRESS', 'REVIEW']
                    ).count(),
                    'by_priority': task_by_priority,
                    'by_status': task_by_status,
                },
                'time_tracking': {
                    'total_estimated': total_time_estimated,
                    'total_logged': total_time_logged,
                    'efficiency': round((total_time_logged / total_time_estimated * 100) if total_time_estimated > 0 else 0, 2)
                },
                'projects': {
                    'total': my_projects.count(),
                    'active': my_projects.filter(status__in=['in_progress', 'review']).count(),
                    'completed': my_projects.filter(status='completed').count(),
                    'stats': project_stats
                },
                'recent_activities': activities
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_mentions(content):
    """Extract @mentions from text content."""
    import re
    pattern = r'@(\w+)'
    matches = re.findall(pattern, content)
    return list(set(matches))  # Remove duplicates


def get_file_type(extension):
    """Determine file type from extension."""
    image_exts = {'jpg', 'jpeg', 'png', 'gif', 'bmp'}
    doc_exts = {'pdf', 'doc', 'docx', 'txt'}
    sheet_exts = {'xls', 'xlsx'}
    slide_exts = {'ppt', 'pptx'}

    if extension in image_exts:
        return 'image'
    elif extension in doc_exts:
        return 'document'
    elif extension in sheet_exts:
        return 'spreadsheet'
    elif extension in slide_exts:
        return 'presentation'
    else:
        return 'archive'
