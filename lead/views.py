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

@group_required(const.LEAD)
def dashboard(request):
    if request.user.is_authenticated:
        request.session['user_role'] = app_views.get_role(request)
        return render(request,'lead/lead.html', lead_dashboard(request))
    else: return redirect('signin')

def admin_dashboard(request):
    if request.user.is_authenticated and request.session['user_role'] == const.LEAD and request.user.is_staff and request.user.username == 'abi':
        return render(request, 'lead/admin-dashboard.html')
    else:
        return redirect('/signout')

@group_required(const.LEAD)
def create_project(request):
    if request.method == 'POST':
        project_name = request.POST['project-name']
        project_description = request.POST['project-description']
        project_client_name = request.POST['project-client_name']
        project_due = request.POST['project-due']
        app_models.Project.objects.create(name=project_name, description=project_description, client_name=project_client_name, due=project_due)
        return redirect('view-projects')
    return render(request, 'lead/create_project.html')

@group_required(const.LEAD)
def assign_project_manager(request):
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
def create_task(request):
    import datetime
    if request.method == 'POST':
        task_name = request.POST['task-name']
        task_description = request.POST['task-description']
        projectid = request.POST['project_id']
        due = request.POST['task-due']
        project = app_models.Project.objects.filter(id=projectid).first()
        task = app_models.Task.objects.create(
            name=task_name,
            description=task_description,
            project=project,
            status=const.TASK_TODO,
            due=due
        )
        if not project.started:
            import datetime
            task.started = datetime.datetime.now()
        project.save()
        return JsonResponse({'status': 200})
    return render(request, 'lead/create_task.html')

@group_required(const.LEAD)
def create_common_task(request):
    task_name = request.POST.get('task_name')
    task_description = request.POST.get('task_description')
    task_user = request.POST.get('task_user', None)
    task_project = request.POST.get('task_project', None)
    if task_user:
        task_user = app_models.User.objects.get(username=task_user)
    if task_project:
        task_project = app_models.Project.objects.get(id=task_project)
    task_due = request.POST.get('task_due')
    task = {
        'name': task_name,
        'description': task_description,
        'due': task_due,
    }
    message = 'Task Created Successfully'
    if task_user:
        task['assigned_to'] = task_user
        message = 'Task Created and Assigned Successfully'
    if task_project:
        task['project'] = task_project
    if task.get('project'):
        app_models.Task.objects.create(**task)
    else:
        app_models.PersonalTask.objects.create(**task)
    messages.success(request, message)
    return JsonResponse({'redirect': request.get_full_path()})

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

@group_required(const.LEAD)
def view_members(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        peers = User.objects.filter(groups__name=const.PEER, is_active=True)
        leads = User.objects.filter(groups__name=const.LEAD, is_active=True)
        managers = User.objects.filter(groups__name=const.MANAGER, is_active=True)
        inactives = User.objects.filter(is_active=False)
        leads_dict = []
        managers_dict = []
        peers_dict = []
        inactives_dict = []
        for lead in leads:
            lead = util.as_dict(lead)
            leads_dict.append(lead)
        for manager in managers:
            manager = util.as_dict(manager)
            managers_dict.append(manager)
        for peer in peers:
            peer = util.as_dict(peer)
            peers_dict.append(peer)
        for inactive in inactives:
            role = app_models.Profile.objects.filter(user=inactive).first()
            if role:
                role = role.role
            inactive = util.as_dict(inactive)
            inactive['role'] = role
            inactives_dict.append(inactive)
        return JsonResponse({'inactives': inactives_dict, 'leads': leads_dict, 'managers': managers_dict, 'peers': peers_dict})
    return render(request, 'lead/view_members.html')

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
def delete_user(request):
    user_id = request.POST.get('userid')
    lead = User.objects.filter(id=request.user.id).first()
    if lead:
        User.objects.filter(id=user_id).delete()
    return JsonResponse({'status': 200})

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