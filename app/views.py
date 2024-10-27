from app.decorators import login_required, group_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from constants import constants as const
from django.http import JsonResponse
from django.contrib import messages
from .models import Project, Task, Profile
from utils import utility
from .mail_server import MailServer
# abiraj asrif420

def index(request):
    if request.user.is_authenticated:
        try:
            request.session['user_role'] = get_role(request)
            return redirect(get_role(request))
        except:
            return redirect('/signout')
    else:
        return redirect('signin')

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def csrf_error_view(request, exception):
    return render(request, '403.html', status=403)

def get_role(request):
    if request.user.is_authenticated:
        try:
            role = request.user.groups.all()[0].name
            role = role.lower()
            return role
        except:
            messages.error(request, 'User not found')
            return "/signout"
    else:
        return "/signin"

def signup(request):
    if request.user.is_authenticated:return render(request,'index.html')
    elif request.method=="POST":
        username = request.POST['username']
        email = request.POST['email']
        role = str(request.POST['role']).lower()
        password = request.POST['password']
        if User.objects.filter(username=username).exists() and User.objects.filter(email=email).exists(): messages.error(request, 'Username and Email already exists')
        elif User.objects.filter(username=username).exists(): messages.error(request, 'Username already exists')
        elif User.objects.filter(email=email).exists(): messages.error(request, 'Email already exists')
        else:
            if role:
                user = User.objects.create_user(username, email, password, is_active=False)
                group = Group.objects.all().filter(name=role).first()
                user.groups.add(group)
                Profile.objects.create(user=user, role=role)
                messages.success(request, 'User created successfully')
                return redirect('signin')
            else:
                messages.error(request, 'Invalid user role')
            return redirect('/signin')
        return redirect("signup")
    else:return render(request,'signup.html')

def signin(request):
    if request.user.is_authenticated:return render(request,'index.html')
    elif request.method == 'POST':    
        username = str(request.POST["username"]).lower()
        password = request.POST["password"]
        filter_dict = {}
        if '@' and '.' in username:
            username['email'] = username
        else: filter_dict['username'] = username
        user = User.objects.filter(**filter_dict).first()
        if user and not user.is_superuser:
            if not user.is_active: messages.error(request, 'User needs to be approved')
            elif authenticate(request, username=username, password=password):
                login(request, user)
                role = get_role(request)
                request.session['user_role'] = role
                return redirect(role)
        else: messages.error(request, 'User not found')
        return redirect("signin")
    else: return render(request,'signin.html')

def signout(request):
    if request.user.is_authenticated:logout(request)
    return redirect('signin')

def get_peers(request):
    peer_name = request.POST.get("peer_name")
    users = list(User.objects.filter(username__icontains=peer_name).values_list('username', flat=True))
    return JsonResponse({"users": users})

@login_required(login_url='/signin')
def get_projects(request):
    role = get_role(request)
    if role == const.LEAD:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(manager=request.user)
    projects_dict = []
    for project in projects:
        project = utility.as_dict(project)
        projects_dict.append(project)
    return JsonResponse({"projects": projects_dict})

@login_required(login_url='/signin')
def get_tasks(request, projectid):
    project = Project.objects.filter(id=projectid).first()
    tasks = Task.objects.filter(project=project)
    tasks_dict = []
    for task in tasks:
        if task.assigned_to:
            assigned_user = task.assigned_to.username
        else:
            assigned_user = None
        task = utility.as_dict(task)
        task['assigned'] = assigned_user
        tasks_dict.append(task)
    return JsonResponse({"tasks": tasks_dict})

@login_required(login_url='/signin')
def get_task_list(request):
    role = get_role(request)
    if role == const.LEAD:
        tasks = Task.objects.all()
    elif role == const.MANAGER:
        tasks = Task.objects.filter(project__manager=request.user)
    else:
        tasks = Task.objects.filter(assigned_to=request.user)
    tasks_dict = []
    for task in tasks:
        if task.assigned_to:
            assigned_user = task.assigned_to.username
        else:
            assigned_user = None
        project_name = task.project.name
        task = utility.as_dict(task)
        task['assigned'] = assigned_user
        task['project'] = project_name
        tasks_dict.append(task)
    return JsonResponse({"tasks": tasks_dict})

def get_project_tasks(request):
    projectid = request.POST.get('projectid')
    if get_role(request) == "peer":
        tasks = Task.objects.filter(project_id=projectid, assigned_to=request.user)
    else:
        tasks = Task.objects.filter(project_id=projectid)
    role = get_role(request)
    tasks_dict = []
    for task in tasks:
        if task.assigned_to:
            assigned_user = task.assigned_to.username
        else:
            assigned_user = None
        project_name = task.project.name
        task = utility.as_dict(task)
        task['assigned'] = assigned_user
        task['project'] = project_name
        tasks_dict.append(task)
    return JsonResponse({"tasks": tasks_dict, "role": role})

@login_required(login_url='/signin')
def search_users(request):
    query = request.GET.get('query', '')
    users = User.objects.filter(username__icontains=query, is_active=True, is_staff=False, is_superuser=False).exclude(groups__name=const.LEAD)[:5]
    users_list = [{'id': user.id, 'username': user.username} for user in users]
    return JsonResponse({'users': users_list})

@login_required(login_url='/signin')
def update_task_status(request):
    task_status = request.POST.get('status')
    task_id = request.POST.get('taskid')
    task = Task.objects.filter(id=task_id).first()
    projectid = task.project.id
    task.status = task_status
    if not task.started:
        task.started = utility.get_current_time()
    task.save()
    return JsonResponse({'status': 200, 'projectid': projectid})

@login_required(login_url='/signin')
def profile(request):
    return render(request, 'profile.html', {'user': request.user})

@login_required(login_url='/signin')
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    return render(request, 'edit_profile.html', {'user': request.user})

@login_required(login_url='/signin')
def send_task_mail(request, user=None, task=None, userid=None, taskid=None):
    if (userid and taskid) and not (user and task):
        user = User.objects.filter(id=userid).first()
        task = Task.objects.filter(id=taskid).first()
    user_name = user.first_name or user.username
    context = const.task_mail_context(task, user_name)
    mailserver = MailServer()
    result = mailserver.send_mail(to_mail=user.email, subject=context['subject'], message=context['message'])
    return JsonResponse({'status': result['status'], 'message': result['message']})

@login_required(login_url='/signin')
def assign_task(request):
    user_id = request.POST.get('user_id')
    task_id = request.POST.get('task_id')
    task = Task.objects.get(id=task_id)
    user = User.objects.get(id=user_id)
    task.assigned_to = user
    task.save()
    send_task_mail(request, user=user, task=task)
    return JsonResponse({'project_id': task.project.id})

@login_required(login_url='/signin')
def view_project(request):
    projectid = request.POST.get('projectid')
    request.session['project_id'] = projectid
    role = request.session.get('user_role')
    return JsonResponse({'status': 200, 'url': f"/{role}/view-project/{projectid}"})

def task_detail(request):
    taskid = request.GET.get('taskid', '')
    task = Task.objects.get(id=taskid)
    if task.project:
        project = task.project.name
    if task.assigned_to:
        assigned = task.assigned_to.username
    else:
        assigned = "Not Assigned"
    task = utility.as_dict(task)
    task['assigned'] = assigned
    task['project'] = project
    return JsonResponse({"task": task})

def sort_tasks_by_status(request):
    status = str(request.POST.get("status")).upper()
    if status == const.TASK_TODO:
        status = const.TASK_TODO
    elif status == const.TASK_PROGRESS:
        status = const.TASK_PROGRESS
    elif status == const.TASK_VERIFY:
        status = const.TASK_VERIFY
    elif status == const.TASK_CORRECTION:
        status = const.TASK_CORRECTION
    elif status == const.TASK_HOLD:
        status = const.TASK_HOLD
    elif status == const.TASK_COMPLETE:
        status = const.TASK_COMPLETE

    if status == const.TASK_ALL:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(status=status)
    if not tasks:
        return JsonResponse({"tasks": [], "status": 400})
    tasks_dict = []
    for task in tasks:
        if task.assigned_to:
            assigned_user = task.assigned_to.username
        else:
            assigned_user = None
        project_name = task.project.name
        task = utility.as_dict(task)
        task['assigned'] = assigned_user
        task['project'] = project_name
        tasks_dict.append(task)
    return JsonResponse({"tasks": tasks_dict, "status": status})

@group_required(const.LEAD)
def delete_project(request):
    projectid = request.POST.get('projectid')
    Project.objects.filter(id=projectid).delete()
    return redirect('view-projects')

@group_required(const.LEAD)
def delete_task(request):
    taskid = request.POST.get('taskid')
    task = Task.objects.get(id=taskid)
    projectid = task.project.id
    task.delete()
    return JsonResponse({"projectid": projectid})

@group_required(const.LEAD, const.MANAGER)
def remove_assigned_peer(request):
    task_id = request.POST.get('taskid')
    task = Task.objects.get(id=task_id)
    project_id = task.project.id
    task.assigned_to = None
    task.save()
    return JsonResponse({'project_id': project_id})
    
def add_task_pull_request(request):
    task_id = request.POST.get('taskid')
    pull_request = request.POST.get('pull_request')
    task = Task.objects.get(id=task_id)
    task.pull_request = pull_request
    task.status = const.TASK_VERIFY
    task.save()
    return JsonResponse({'projectid': task.project.id})

def add_task_correction(request):
    task_id = request.POST.get('taskid')
    correction = request.POST.get('correction')
    task = Task.objects.get(id=task_id)
    task.correction = correction
    task.status = const.TASK_CORRECTION
    task.save()
    return JsonResponse({'projectid': task.project.id})

def hold_task(request):
    task_id = request.POST.get('taskid')
    reason = request.POST.get('reason')
    task = Task.objects.get(id=task_id)
    task.status = const.TASK_HOLD
    task.reason = reason
    task.save()
    return JsonResponse({'projectid': task.project.id})

@group_required(const.LEAD, const.MANAGER)
def change_project_status(request):
    status = request.POST.get('status')
    project_id = request.POST.get('project_id')
    try:
        project = Project.objects.get(id=project_id)
        project.status = status
        if status == const.TASK_COMPLETE:
            total_tasks = Task.objects.filter(project=project).count()
            completed_tasks = Task.objects.filter(project=project, status=const.TASK_COMPLETE).count()
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