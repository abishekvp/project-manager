from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt
from app import views as app_views

urlpatterns = [
    path('', views.dashboard, name='lead'),
    path('admin-dashboard', views.admin_dashboard, name='admin-dashboard'),
    path('view-members', views.view_members, name='view-members'),
    path('delete-member', views.delete_member, name='delete-member'),
    path('create-project', views.create_project, name='create-project'),

    path('create-task', views.create_task, name='create-task'),
    path('view-projects', views.view_projects, name='view-projects'),
    path('view-project/<int:projectid>', views.view_project, name='lead-view-project'),
    path('delete-task/<int:projectid>/<int:taskid>/', views.delete_task, name='delete-task'),
    path('view-tasks', views.view_tasks, name='lead-tasks'),
    
    path('mail-server', views.view_mail_server, name='mail-server'),
    path('test-mail-server', views.test_mail_server, name='test-mail-server'),
    path('inactive-user', views.inactive_user, name='inactive-user'),
    path('approve-user', views.approve_user, name='approve-user'),
    path('configure-mail-server', views.configure_mail_server, name='configure-mail-server'),
    path('assign-project', views.assign_project_manager, name='assign-project'),
    path('remove-project-manager', views.remove_project_manager, name='remove-project-manager'),
    path('search-manager/', views.search_manager, name='search-manager'),
    path('get-all-tasks-table', views.get_all_tasks_table, name='get-all-tasks-table'),
]
