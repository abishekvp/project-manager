from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
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
@login_required(login_url='/signin/')
def index(request):
    if request.user.is_authenticated:
        request.session['user_role'] = get_role(request)
        return redirect(get_role(request))
    else:
        return redirect('signin')

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def csrf_error_view(request, exception):
    return render(request, '403.html', status=403)

def get_role(request):
    if request.user.is_authenticated:
        role = request.user.groups.all()[0].name
        role = role.lower()
        return role
    else: return ""

def signup(request):
    if request.user.is_authenticated:return render(request,'index.html')
    elif request.method=="POST":
        username = request.POST['username']
        email = request.POST['email']
        role = str(request.POST['role']).upper()
        password = request.POST['password']
        if User.objects.filter(username=username).exists() and User.objects.filter(email=email).exists(): messages.error(request, 'Username and Email already exists')
        elif User.objects.filter(username=username).exists(): messages.info(request, 'Username already exists')
        elif User.objects.filter(email=email).exists(): messages.info(request, 'Email already exists')
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
        username = request.POST["username"]
        password = request.POST["password"]
        if '@' in username: username = User.objects.get(email=username.lower()).username
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            role = get_role(request)
            request.session['user_role'] = role
            return redirect(role)
        else: messages.error(request, 'User not found')
        return redirect("signin")
    else:return render(request,'signin.html')

def signout(request):
    if request.user.is_authenticated:logout(request)
    return redirect('signin')

def lead(request):
    if request.user.is_authenticated and get_role(request)=="lead":
        return redirect('lead')
    else: return redirect('signin')

def peer(request):
    if request.user.is_authenticated and get_role(request)=="peer":
        return redirect('peer')
    else: return redirect('signin')

def get_peers(request):
    peer_name = request.POST.get("peer_name")
    users = list(User.objects.filter(username__icontains=peer_name).values_list('username', flat=True))
    return JsonResponse({"users": users})

def get_projects(request):
    projects = Project.objects.all()
    projects_dict = []
    for project in projects:
        project = utility.as_dict(project)
        projects_dict.append(project)
    return JsonResponse({"projects": projects_dict})

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

def search_users(request):
    query = request.GET.get('query', '')
    users = User.objects.filter(username__icontains=query)[:5]
    users_list = [{'id': user.id, 'username': user.username} for user in users]
    return JsonResponse({'users': users_list})

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

def profile(request):
    return render(request, 'profile.html', {'user': request.user})

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

def send_task_mail(userid, taskid):
    user = User.objects.filter(id=userid).first()
    task = Task.objects.filter(id=taskid).first()
    user_name = user.first_name or user.username
    context = const.task_mail_context(task, user_name)
    mailserver = MailServer()
    mailserver.send_mail(to_mail=user.email, subject=context['subject'], message=context['message'])
    return JsonResponse({'status': 200})

def assign_task(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        task_id = request.POST.get('task_id')
        task = Task.objects.get(id=task_id)
        peer = User.objects.get(id=user_id)
        task.assigned_to = peer
        task.save()
        send_task_mail(user_id, task_id)
        project_id = request.session.get('project_id')
        return JsonResponse({'status': 200, 'project_id': project_id})
    users = User.objects.all()
    return render(request, 'assign_task.html', {'task': task, 'users': users})

def view_project(request):
    projectid = request.POST.get('projectid')
    request.session['project_id'] = projectid
    role = request.session.get('user_role')
    return JsonResponse({'status': 200, 'url': f"/{role}/view-project/{projectid}/"})