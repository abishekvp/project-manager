from django.db.models import Q
from app.decorators import group_required
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from app import models as app_models, views as app_views
from django.contrib import messages
from django.http import JsonResponse
from constants import constants as const
from utils import utility as util
from django.utils import timezone

@group_required(const.MANAGER)
def dashboard(request):
    if request.user.is_authenticated:
        request.session['user_role'] = app_views.get_role(request)
        return render(request,'manager/dashboard.html', manager_dashboard(request))
    else: return redirect('signin')

@group_required(const.MANAGER)
def create_task(request):
    if request.method == 'POST':
        task_name = request.POST.get('task_name')
        task_description = request.POST.get('task_description')
        task_user = request.POST.get('task_user')
        task_project = request.POST.get('task_project')
        task_due = request.POST.get('task_due')
        task = dict()
        task['name'] = task_name
        task['description'] = task_description
        if task_project:
            project = app_models.Project.objects.get(id=task_project)
            if not project.started:
                project.started = timezone.localtime(timezone.now())
            project.save()
            task['project'] = project
        if task_user:
            task['assigned_to'] = User.objects.get(id=task_user)
        if task_due:
            task['due'] = task_due
        app_models.Task.objects.create(**task)
        return JsonResponse({'status': 200})
    else:
        return JsonResponse({'status': 403})

@group_required(const.LEAD, const.MANAGER)
def list_projects(request):
    return render(request, 'manager/list_projects.html')

@group_required(const.LEAD, const.MANAGER)
def view_project(request, projectid):
    project = app_models.Project.objects.filter(id=projectid).first()
    request.session['project_id'] = projectid
    project_dict = util.as_dict(project)
    if project.manager:
        project_dict['manager'] = project.manager.username
    print(project_dict)
    return render(request, 'manager/view_project.html', {"project": project_dict})

@group_required(const.LEAD, const.MANAGER)
def change_project_status(request, projectid):
    if request.method == 'POST':
        status = request.POST.get('status')
        try:
            project = app_models.Project.objects.get(id=projectid)
            project.status = status
            if status == const.TASK_COMPLETE:
                total_tasks = app_models.Task.objects.filter(project=project).count()
                completed_tasks = app_models.Task.objects.filter(project=project, status=const.TASK_COMPLETE).count()
                if total_tasks != completed_tasks:
                    messages.info(request, 'All tasks must be completed before marking project as complete.')
                    return JsonResponse({"error": "All tasks must be completed before marking project as complete."}, status=400)
            if not project.started:
                project.started = timezone.localtime(timezone.now())
            project.save()
            return JsonResponse({"message": "Status updated successfully."})
        except Exception as e:
            return JsonResponse({"error": "Project not found."}, status=404)
    return JsonResponse({"error": "Invalid request."}, status=400)

@group_required(const.LEAD, const.MANAGER)
def delete_task(request, projectid, taskid):
    app_models.Task.objects.filter(id=taskid).delete()
    return redirect(f'/manager/view-project/{projectid}/')

@group_required(const.LEAD, const.MANAGER)
def assign_task(request):
    user_id = request.POST.get('user_id')
    task_id = request.POST.get('task_id')
    task = app_models.Task.objects.get(id=task_id)
    peer = User.objects.get(id=user_id)
    if task and peer:
        task.assigned_to = peer
        task.save()
        app_views.send_task_mail(user_id, task_id)
        project_id = request.session.get('project_id')
        return JsonResponse({'status': 200, 'project_id': project_id})
    return JsonResponse({'status': 400})

@group_required(const.LEAD, const.MANAGER)
def remove_assigned_peer(request):
    if request.method == 'POST':
        task_id = request.POST.get('taskid')
        task = app_models.Task.objects.get(id=task_id)
        task.assigned_to = None
        task.save()
        project_id = request.session.get('project_id')
        return JsonResponse({'project_id': project_id})

@group_required(const.LEAD, const.MANAGER)
def view_tasks(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        projects = app_models.Project.objects.filter(manager=request.user)
        tasks = app_models.Task.objects.filter(
            Q(project__in=projects) | Q(assigned_to__username=request.user)
        )
        tasks_dict = []
        for task in tasks:
            project_name = assigned = None
            if task.project:
                project_name = task.project.name
            if task.assigned_to:
                assigned = task.assigned_to.username
            task = util.as_dict(task)
            task['project'] = project_name
            task['assigned'] = assigned
            tasks_dict.append(task)
        return JsonResponse({'tasks': tasks_dict})
    return render(request, 'manager/view_tasks.html')

@group_required(const.LEAD, const.MANAGER)
def manager_dashboard(request):
    context = {}
    projects = app_models.Project.objects.filter(manager=request.user)
    total_projects = projects.count()
    total_tasks = app_models.Task.objects.all().count()

    context['todo_tasks'] = app_models.Task.objects.filter(status=const.TASK_TODO).count()
    context['progress_tasks'] = app_models.Task.objects.filter(status=const.TASK_PROGRESS).count()
    context['verify_tasks'] = app_models.Task.objects.filter(status=const.TASK_VERIFY).count()
    context['correction_tasks'] = app_models.Task.objects.filter(status=const.TASK_CORRECTION).count()
    context['hold_tasks'] = app_models.Task.objects.filter(status=const.TASK_HOLD).count()
    context['complete_tasks'] = app_models.Task.objects.filter(status=const.TASK_COMPLETE).count()

    project_stats = []
    for project in projects:
        task_status = {}
        tasks = app_models.Task.objects.filter(project=project)
        for task in tasks:
            if task.status not in task_status:
                task_status[task.status] = 1
            else:
                task_status[task.status]
        total_tasks_in_project = tasks.count()
        completed_tasks_in_project = tasks.filter(status=const.TASK_COMPLETE).count()
        hold_tasks_in_project = tasks.filter(status=const.TASK_HOLD).count()
        verify_tasks_in_project = tasks.filter(status=const.TASK_VERIFY).count()

        if total_tasks_in_project > 0:
            completion_percentage = (completed_tasks_in_project / total_tasks_in_project) * 100
        else:
            completion_percentage = 0

        project_stats.append({
            'project': project,
            'total_tasks': total_tasks_in_project,
            'completed_tasks': completed_tasks_in_project,
            'hold_tasks': hold_tasks_in_project,
            'verify_tasks': verify_tasks_in_project,
            'completion_percentage': round(completion_percentage, 2),
        })

    context['project_stats'] = project_stats
    context['total_projects'] = total_projects
    context['total_tasks'] = total_tasks
    return context

def sort_tasks_by_status(request):
    status = request.POST.get('status')
    projects = app_models.Project.objects.filter(manager=request.user)
    if status == const.TASK_ALL:
        tasks = app_models.Task.objects.filter(project__in=projects)
    else:
        tasks = app_models.Task.objects.filter(status=status, project__in=projects)
    tasks_dict = []
    for task in tasks:
        project_name = task.project.name
        assigned = task.assigned_to.username if task.assigned_to else '  ---  '
        task = util.as_dict(task)
        task['project'] = project_name
        task['assigned'] = assigned
        tasks_dict.append(task)
    return JsonResponse({'tasks': tasks_dict})