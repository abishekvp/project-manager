from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt
from app import views as app_views

urlpatterns = [
    path('', views.dashboard, name='lead'),
    path('create-peer', views.create_peer, name='create-peer'),
    path('create-project', views.create_project, name='create-project'),
    path('create-task', views.create_task, name='create-task'),
    path('list-projects', views.list_projects, name='list-projects'),
    path('view-project/<int:projectid>/', views.view_project, name='lead-view-project'),
    path('delete-project/<int:projectid>/', views.delete_project, name='delete-project'),
    path('delete-task/<int:projectid>/<int:taskid>/', views.delete_task, name='delete-task'),
    path('change-project-status/<int:projectid>/', views.change_project_status, name='change-project-status'),
    path('remove-assigned-peer', views.remove_assigned_peer, name='/lead/remove-assigned-peer'),
    path('view-tasks', views.view_tasks, name='view-tasks'),
    path('view-members', views.view_members, name='view-members'),
    path('mail-server', views.mail_server, name='mail-server'),
    path('test-mail-server', views.test_mail_server, name='test-mail-server'),
    path('delete-user', views.delete_user, name='delete-user'),
    path('inactive-user', views.inactive_user, name='inactive-user'),
    path('assign-task', views.app_views.assign_task, name='assign-task'),
    path('approve-user', views.approve_user, name='approve-user'),
    path('configure-mail-server', views.configure_mail_server, name='configure-mail-server'),
]
