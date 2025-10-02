from django.db.models import Q
from django.db import IntegrityError
from app.decorators import group_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.http import JsonResponse
from constants import constants as const
from utils import utility as util
from app import mail_server
from app import views as app_views
from app import models as app_models
from django.utils import timezone


@group_required(const.LEAD)
def dashboard(request):
    if request.user.is_authenticated:
        request.session['user_role'] = app_views.get_role(request)
        return render(request,'lead/dashboard.html', lead_dashboard(request))
    else: return redirect('signin')


def admin_dashboard(request):
    if request.user.is_authenticated and (request.session.get('user_role') == const.LEAD or request.user.is_superuser) and request.user.is_staff:
        return render(request, 'lead/admin-dashboard.html')
    else:
        return redirect('/signout')


@group_required(const.LEAD)
def view_members(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        members = []
        filter_query = Q()
        status = request.GET.get('status', '').lower()
        search = request.GET.get('search', '').lower()
        if search:
            filter_query = (
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        if status:
            if status == const.INACTIVE:
                filter_query &= Q(is_active=False)
            elif status == const.LEAD:
                filter_query &= Q(groups__name=const.LEAD)
            elif status == const.MANAGER:
                filter_query &= Q(groups__name=const.MANAGER)
            elif status == const.PEER:
                filter_query &= Q(groups__name=const.PEER)
        filter_query &= ~Q(groups__name=const.VENDOR)
        filter_query &= ~Q(groups__name=const.ADMINISTER)
        users = User.objects.filter(filter_query).exclude(is_superuser=True)
        for user in users:
            user_dict = util.as_dict(user)
            user_dict['role'] = user.groups.first().name
            members.append(user_dict)
        return JsonResponse({'members': members})
    return render(request, 'lead/view_members.html')


@group_required(const.LEAD)
def delete_member(request):
    user_id = request.POST.get('userid')
    user = User.objects.filter(id=user_id).exclude(username="abi")
    if user:
        try:
            user.delete()
        except IntegrityError:
            messages.error(request, 'User is assigned to some tasks or projects. Please reassign the work before deleting the user.')
            return JsonResponse({'status': 403})
    return JsonResponse({'status': 200})


# projects views
@group_required(const.LEAD)
def create_project(request):
    if request.method == 'POST':
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        client_name = request.POST.get('project_client')
        due = request.POST.get('project_due')
        project = {
            "name": project_name,
            "description": project_description,
        }
        if client_name:
            project['client_name'] = client_name
        if due:
            project['due'] = due
        app_models.Project.objects.create(**project)
        messages.success(request, 'Project created successfully.')
        return JsonResponse({'status': 200})
    return render(request, 'lead/create_project.html')

@group_required(const.LEAD)
def delete_project(request):
    project_id = request.POST.get('project_id')
    app_models.Project.objects.filter(id=project_id).delete()
    return JsonResponse({'status': 200})

@group_required(const.LEAD)
def assign_project_manager(request):
    import time
    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        manager_id = request.POST.get('manager_id')
        project = app_models.Project.objects.get(id=project_id)
        project.manager = User.objects.get(id=manager_id)
        project.save()
        result = mail_server.send_project_assigned_mail(project, project.manager)
        return JsonResponse({'project_id': project_id})

@group_required(const.LEAD)
def remove_project_manager(request):
    if request.method == 'POST':
        project_id = request.POST.get('projectid')
        project = app_models.Project.objects.get(id=project_id)
        project.manager = None
        project.save()
        return JsonResponse({'project_id': project_id})

@group_required(const.LEAD)
def view_projects(request):
    return render(request, 'lead/list_projects.html')

@group_required(const.LEAD)
def view_project(request, projectid):
    project = app_models.Project.objects.get(id=projectid)
    manager = project.manager
    project = util.as_dict(project)
    if manager:
        project['manager'] = manager.username
    else:
        project['manager'] = None
    return render(request, 'lead/view_project.html', {"project": project})

@group_required(const.LEAD)
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

@group_required(const.LEAD)
def delete_task(request, projectid, taskid):
    app_models.Task.objects.filter(id=taskid).delete()
    return redirect(f'/lead/view-project/{projectid}/')

@group_required(const.LEAD)
def view_tasks(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        tasks = app_models.Task.objects.all()
        tasks_dict = []
        for task in tasks:
            project_name = task.project.name
            assigned = task.assigned_to.username if task.assigned_to else '  ---  '
            task = util.as_dict(task)
            task['project'] = project_name
            task['assigned'] = assigned
            tasks_dict.append(task)
        return JsonResponse({'tasks': tasks_dict})
    return render(request, 'lead/view_tasks.html')

def get_all_tasks_table(request):
    tasks = app_models.Task.objects.all()
    for task in tasks:
        task_dict = util.as_dict(task)
        if task.project:
            task_dict["project"] = task.project.name
        if task.assigned_to:
            task_dict["assigned"] = task.assigned_to.username
        tasks.append(task_dict)
    return JsonResponse({"tasks": tasks})

@group_required(const.LEAD)
def lead_dashboard(request):
    context = {}
    projects = app_models.Project.objects.all()
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

@group_required(const.LEAD)
def view_mail_server(request):
    mail_settings = app_models.MailServer.objects.first()
    if mail_settings:
        mail_settings = util.as_dict(mail_settings)
    return render(request, 'lead/mail-server.html', {'mail_settings': mail_settings})

@group_required(const.LEAD)
def configure_mail_server(request):
    if request.method == 'POST':
        smtp_server = request.POST['smtp_server']
        smtp_port = request.POST['smtp_port']
        username = request.POST['username']
        password = request.POST['password']
        from_mail = request.POST['from_mail']
        mail_setting = app_models.MailServer.objects.first()
        if not mail_setting:
            mail_setting = app_models.MailServer()
        mail_setting.server = smtp_server
        mail_setting.port = smtp_port
        mail_setting.username = username
        mail_setting.password = password
        mail_setting.from_email = from_mail
        mail_setting.save()
        mailserver = mail_server.MailServer()
        mailserver.login_server(server=smtp_server, port=smtp_port, username=username, password=password, from_email=from_mail)
        messages.success(request, 'Mail server configured successfully.')
        return redirect('mail-server')
    mail_settings = app_models.MailServer.objects.first()
    if mail_settings:
        mail_settings = util.as_dict(mail_settings)
    return render(request, 'lead/configure-mail-server.html', {'mail_settings': mail_settings})

@group_required(const.LEAD)
def test_mail_server(request):
    server = request.POST.get('smtp_server')
    port = request.POST.get('smtp_port')
    username = request.POST.get('username')
    password = request.POST.get('password')
    from_email = request.POST.get('from_mail')
    to_mail = request.POST.get('to_mail')
    mailserver = mail_server.MailServer()
    response = mailserver.login_server(server=server, port=port, username=username, password=password, from_email=from_email)
    context = const.test_mail_context()
    mail = mailserver.send_mail(to_mail=to_mail, subject=context['subject'], message=context['message'])
    if response['status'] == 200 and mail['status'] == 200:
        return JsonResponse({'status': 200, 'message': 'Mail sent successfully.'})
    else:
        return JsonResponse({'status': 500, 'message': 'Failed to configure mail server.'})


@group_required(const.LEAD)
def inactive_user(request):
    user_id = request.POST.get('userid')
    user = User.objects.filter(id=user_id).first()
    if user:
        user.is_active = False
        user.save()
    return JsonResponse({'status': 200})

@group_required(const.LEAD)
def approve_user(request):
    user_id = request.POST.get('userid')
    user = User.objects.filter(id=user_id).first()
    if user:
        user.is_active = True
        user.is_staff = True
        user.save()
    return JsonResponse({'status': 200})

@group_required(const.LEAD)
def search_manager(request):
    query = request.GET.get('query', '')
    managers = User.objects.filter(username__icontains=query, groups__name=const.MANAGER, is_active=True)[:5]
    managers_list = [{'id': user.id, 'username': user.username} for user in managers]
    return JsonResponse({'managers': managers_list})