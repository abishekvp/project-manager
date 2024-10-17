from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from app import models as app_models, views as app_views
from django.contrib import messages
from django.http import JsonResponse
from constants import constants as const
from utils import utility as util
from app.mail_server import MailServer
from app.views import get_role

@login_required(login_url='/signin')
def dashboard(request):
    if request.user.is_authenticated:
        request.session['user_role'] = get_role(request)
        return render(request,'lead/lead.html', lead_dashboard(request))
    else: return redirect('signin')

def create_peer(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        user = User.objects.create_user(username=username, email=email, password=username)
        group = Group.objects.all().filter(name=const.PEER).first()
        user.groups.add(group)
        return redirect('view-peers')
    return render(request, 'lead/create_peer.html')

def create_project(request):
    if request.method == 'POST':
        project_name = request.POST['project-name']
        project_description = request.POST['project-description']
        project_client_name = request.POST['project-client_name']
        project_due = request.POST['project-due']
        app_models.Project.objects.create(name=project_name, description=project_description, client_name=project_client_name, due=project_due)
        return redirect('list-projects')
    return render(request, 'lead/create_project.html')

def delete_project(request, projectid):
    app_models.Project.objects.filter(id=projectid).delete()
    return redirect('list-projects')

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

def list_projects(request):
    return render(request, 'lead/list_projects.html')

def view_project(request, projectid):
    project = app_models.Project.objects.filter(id=projectid).first()
    project = util.as_dict(project)
    return render(request, 'lead/view_project.html', {"project": project})

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
                import datetime
                project.started = datetime.datetime.now()
            project.save()
            return JsonResponse({"message": "Status updated successfully."})
        except Exception as e:
            return JsonResponse({"error": "Project not found."}, status=404)
    return JsonResponse({"error": "Invalid request."}, status=400)

def delete_task(request, projectid, taskid):
    app_models.Task.objects.filter(id=taskid).delete()
    return redirect(f'/lead/view-project/{projectid}/')

def remove_assigned_peer(request):
    if request.method == 'POST':
        task_id = request.POST.get('taskid')
        task = app_models.Task.objects.get(id=task_id)
        task.assigned_to = None
        task.save()
        project_id = request.session.get('project_id')
        return JsonResponse({'project_id': project_id})

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

def mail_server(request):
    mail_settings = app_models.MailServer.objects.first()
    if mail_settings:
        mail_settings = util.as_dict(mail_settings)
    return render(request, 'lead/mail-server.html', {'mail_settings': mail_settings})

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
        mailserver = MailServer()
        mailserver.login_server(server=smtp_server, port=smtp_port, username=username, password=password, from_email=from_mail)
        messages.success(request, 'Mail server configured successfully.')
        return redirect('mail-server')
    mail_settings = app_models.MailServer.objects.first()
    if mail_settings:
        mail_settings = util.as_dict(mail_settings)
    return render(request, 'lead/configure-mail-server.html', {'mail_settings': mail_settings})

def test_mail_server(request):
    server = request.POST.get('smtp_server')
    port = request.POST.get('smtp_port')
    username = request.POST.get('username')
    password = request.POST.get('password')
    from_email = request.POST.get('from_mail')
    to_mail = request.POST.get('to_mail')
    mailserver = MailServer()
    response = mailserver.login_server(server=server, port=port, username=username, password=password, from_email=from_email)
    context = const.test_mail_context()
    mail = mailserver.send_mail(to_mail=to_mail, subject=context['subject'], message=context['message'])
    if response['status'] == 200 and mail['status'] == 200:
        return JsonResponse({'status': 200, 'message': 'Mail sent successfully.'})
    else:
        return JsonResponse({'status': 500, 'message': 'Failed to configure mail server.'})
    
def delete_user(request):
    user_id = request.POST.get('userid')
    lead = User.objects.filter(id=request.user.id).first()
    if lead:
        User.objects.filter(id=user_id).delete()
    return JsonResponse({'status': 200})

def inactive_user(request):
    user_id = request.POST.get('userid')
    user = User.objects.filter(id=user_id).first()
    if user:
        user.is_active = False
        user.save()
    return JsonResponse({'status': 200})

def approve_user(request):
    user_id = request.POST.get('userid')
    user = User.objects.filter(id=user_id).first()
    if user:
        user.is_active = True
        user.save()
    return JsonResponse({'status': 200})