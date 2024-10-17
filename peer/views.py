from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from app.models import Project, Task
from utils import utility as util
from django.http import JsonResponse
from constants import constants as const
def dashboard(request):
    if request.user.is_authenticated:
        return render(request,'peer/peer.html', peer_dashboard(request))
    else: return redirect('signin')

def peer_projects(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        tasks = Task.objects.filter(assigned_to=request.user)
        user_projects = Project.objects.filter(id__in=tasks.values('project')).distinct()
        projects_dict = []
        for project in user_projects:
            projects_dict.append(util.as_dict(project))
        return JsonResponse({'projects': projects_dict})
    return render(request, 'peer/list_projects.html')

def peer_tasks(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        tasks = Task.objects.filter(assigned_to=request.user)
        task_dict = []
        for task in tasks:
            project_name = task.project.name
            task = util.as_dict(task)
            task['project'] = project_name
            task_dict.append(task)
        return JsonResponse({'tasks': task_dict})
    return render(request, 'peer/view_tasks.html')

def view_project(request, projectid):
    project = Project.objects.filter(id=projectid).first()
    request.session['project_id'] = projectid
    project = util.as_dict(project)
    return render(request, 'peer/peer_project.html', {"project": project})

def peer_dashboard(request):
    user = request.user  # Get the currently logged-in user
    context = {}

    # Filter projects and tasks based on the logged-in user
    tasks = Task.objects.filter(assigned_to=request.user)
    projects = Project.objects.filter(id__in=tasks.values('project')).distinct()
    total_projects = projects.count()
    
    # Filter tasks that belong to the logged-in user's projects
    total_tasks = Task.objects.filter(assigned_to=user).count()

    # Task counts by status, only for the user's projects
    context['todo_tasks'] = Task.objects.filter(assigned_to=user, status=const.TASK_TODO).count()
    context['progress_tasks'] = Task.objects.filter(assigned_to=user, status=const.TASK_PROGRESS).count()
    context['verify_tasks'] = Task.objects.filter(assigned_to=user, status=const.TASK_VERIFY).count()
    context['correction_tasks'] = Task.objects.filter(assigned_to=user, status=const.TASK_CORRECTION).count()
    context['hold_tasks'] = Task.objects.filter(assigned_to=user, status=const.TASK_HOLD).count()
    context['complete_tasks'] = Task.objects.filter(assigned_to=user, status=const.TASK_COMPLETE).count()

    # Prepare project statistics, only for the logged-in user
    project_stats = []
    for project in projects:
        task_status = {}
        tasks = Task.objects.filter(project=project)
        for task in tasks:
            if task.status not in task_status:
                task_status[task.status] = 1
            else:
                task_status[task.status] += 1  # You missed incrementing the value here

        total_tasks_in_project = tasks.count()
        completed_tasks_in_project = tasks.filter(status=const.TASK_COMPLETE).count()
        hold_tasks_in_project = tasks.filter(status=const.TASK_HOLD).count()
        verify_tasks_in_project = tasks.filter(status=const.TASK_VERIFY).count()

        # Calculate completion percentage for the project
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

    # Add statistics and project data to the context
    context['project_stats'] = project_stats
    context['total_projects'] = total_projects
    context['total_tasks'] = total_tasks

    return context
