"""
AJAX API Views for dynamic task and project management
Returns JSON responses for frontend JavaScript
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Task, Project, Assignment
from django.core.paginator import Paginator
import json
from django.utils import timezone

@login_required
@require_http_methods(["GET"])
def api_get_tasks(request):
    """Get tasks with optional filtering"""
    try:
        project_id = request.GET.get('project_id')
        status = request.GET.get('status')
        priority = request.GET.get('priority')
        page = request.GET.get('page', 1)
        per_page = int(request.GET.get('per_page', 20))

        query = Task.objects.all()

        if project_id:
            query = query.filter(project_id=project_id)
        if status:
            query = query.filter(status=status)
        if priority:
            query = query.filter(priority=priority)

        # Get user's tasks
        query = query.filter(assigned_to=request.user) | Task.objects.filter(project__manager=request.user)
        query = query.distinct().order_by('-created')

        paginator = Paginator(query, per_page)
        page_obj = paginator.get_page(page)

        tasks = []
        for task in page_obj:
            tasks.append({
                'id': task.id,
                'name': task.name,
                'description': task.description,
                'project': task.project.name,
                'project_id': task.project_id,
                'status': task.status,
                'priority': task.priority,
                'due_date': task.due.isoformat() if task.due else None,
                'assigned_to': task.assigned_to.username if task.assigned_to else None,
                'time_estimate': task.time_estimate,
                'time_logged': task.time_logged,
                'progress': int((task.time_logged / task.time_estimate * 100) if task.time_estimate else 0),
            })

        return JsonResponse({
            'success': True,
            'tasks': tasks,
            'total': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_http_methods(["GET"])
def api_get_projects(request):
    """Get projects for current user"""
    try:
        page = request.GET.get('page', 1)
        per_page = int(request.GET.get('per_page', 10))

        # Get projects where user is manager or assigned to tasks
        projects = Project.objects.filter(manager=request.user) | Project.objects.filter(task__assigned_to=request.user)
        projects = projects.distinct().order_by('-created')

        paginator = Paginator(projects, per_page)
        page_obj = paginator.get_page(page)

        project_data = []
        for project in page_obj:
            total_tasks = project.task_set.count()
            completed_tasks = project.task_set.filter(status='COMPLETE').count()
            progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            project_data.append({
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'status': project.status,
                'priority': project.priority,
                'client_name': project.client_name,
                'due_date': project.due.isoformat() if project.due else None,
                'progress': int(progress),
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'manager': project.manager.username if project.manager else None,
            })

        return JsonResponse({
            'success': True,
            'projects': project_data,
            'total': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def api_update_task_status(request):
    """Update task status via AJAX"""
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        new_status = data.get('status')

        task = get_object_or_404(Task, id=task_id)

        # Authorization check
        if task.assigned_to != request.user and task.project.manager != request.user:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

        task.status = new_status
        task.updated = timezone.now()
        if new_status not in ['TODO', 'IN_PROGRESS'] and not task.started:
            task.started = timezone.now()
        task.save(update_fields=['status', 'updated', 'started'])

        return JsonResponse({
            'success': True,
            'message': f'Task status updated to {new_status}',
            'task': {
                'id': task.id,
                'status': task.status,
                'updated': task.updated.isoformat()
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def api_log_task_time(request):
    """Log time spent on task"""
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        minutes = int(data.get('minutes', 0))

        task = get_object_or_404(Task, id=task_id)

        if task.assigned_to != request.user and task.project.manager != request.user:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

        task.time_logged += minutes
        task.save(update_fields=['time_logged'])

        progress = int((task.time_logged / task.time_estimate * 100) if task.time_estimate else 0)

        return JsonResponse({
            'success': True,
            'message': f'Logged {minutes} minutes',
            'task': {
                'id': task.id,
                'time_logged': task.time_logged,
                'progress': progress
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_http_methods(["GET"])
def api_get_dashboard_stats(request):
    """Get dashboard statistics"""
    try:
        user = request.user

        # My tasks
        my_tasks = Task.objects.filter(assigned_to=user)
        my_projects = Project.objects.filter(manager=user)

        stats = {
            'total_tasks': my_tasks.count(),
            'in_progress_tasks': my_tasks.filter(status='IN_PROGRESS').count(),
            'completed_tasks': my_tasks.filter(status='COMPLETE').count(),
            'overdue_tasks': my_tasks.filter(due__lt=timezone.now().date()).exclude(status='COMPLETE').count(),
            'total_projects': my_projects.count(),
            'active_projects': my_projects.filter(status__in=['in_progress', 'review']).count(),
            'completed_projects': my_projects.filter(status='completed').count(),
        }

        # Recent tasks
        recent_tasks = my_tasks.order_by('-updated')[:5]
        recent = []
        for task in recent_tasks:
            recent.append({
                'id': task.id,
                'name': task.name,
                'project': task.project.name,
                'status': task.status,
                'priority': task.priority,
                'due_date': task.due.isoformat() if task.due else None,
            })

        stats['recent_tasks'] = recent

        return JsonResponse({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def api_update_task_priority(request):
    """Update task priority"""
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        priority = data.get('priority')

        task = get_object_or_404(Task, id=task_id)

        if task.assigned_to != request.user and task.project.manager != request.user:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

        task.priority = priority
        task.save(update_fields=['priority'])

        return JsonResponse({
            'success': True,
            'message': f'Priority updated to {priority}',
            'task': {'id': task.id, 'priority': task.priority}
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_http_methods(["GET"])
def api_get_kanban_data(request):
    """Get tasks organized by status for kanban view"""
    try:
        project_id = request.GET.get('project_id')

        if project_id:
            tasks = Task.objects.filter(project_id=project_id)
        else:
            tasks = Task.objects.filter(assigned_to=request.user) | Task.objects.filter(project__manager=request.user)
            tasks = tasks.distinct()

        statuses = ['TODO', 'IN_PROGRESS', 'REVIEW', 'COMPLETE']
        kanban = {}

        for status in statuses:
            status_tasks = tasks.filter(status=status).order_by('priority', 'due')
            kanban[status] = []
            for task in status_tasks:
                kanban[status].append({
                    'id': task.id,
                    'name': task.name,
                    'priority': task.priority,
                    'assigned_to': task.assigned_to.username if task.assigned_to else 'Unassigned',
                    'due_date': task.due.isoformat() if task.due else None,
                    'time_estimate': task.time_estimate,
                    'time_logged': task.time_logged,
                })

        return JsonResponse({
            'success': True,
            'kanban': kanban
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
