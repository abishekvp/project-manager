from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.dashboard, name='manager'),
    path('create-task', views.create_task, name='manager-create-task'),
    path('manager-list-projects', views.list_projects, name='manager-list-projects'),
    path('view-project/<int:projectid>/', views.view_project, name='manager-view-project'),
    path('delete-task/<int:projectid>/<int:taskid>/', views.delete_task, name='manager-delete-task'),
    path('change-project-status/<int:projectid>/', views.change_project_status, name='manager-change-project-status'),
    path('remove-assigned-peer', views.remove_assigned_peer, name='manager-remove-assigned-peer'),
    path('view-tasks', views.view_tasks, name='manager-view-tasks'),
]
