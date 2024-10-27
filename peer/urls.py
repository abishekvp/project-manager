from django.urls import path
from . import views
from app import views as app_views

urlpatterns = [
    path('', views.dashboard, name="peer"),
    path('view-projects', views.peer_projects, name="view-peer-projects"),
    path('view-project/<int:projectid>', views.view_project, name="peer-view-project"),
    path('peer-tasks', views.peer_tasks, name="peer-tasks"),
    path('update-task-status', app_views.update_task_status, name="peer-update-task-status"),
    path('sort-tasks-by-status', views.sort_tasks_by_status, name='sort-tasks-by-status'),
]
