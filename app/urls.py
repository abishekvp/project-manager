from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.index,name="index"),
    path('access-restricted', views.access_restricted, name='access-restricted'),
    path('signup', views.signup,name="signup"),
    path('signin/', views.signin,name="signin"),
    path('signout/', views.signout,name="signout"),
    path('search-users/', views.search_users, name='search-users'),
    path('search-projects/', views.search_projects, name='search-projects'),
    path('create-task', views.create_task, name='create-task'),
    path('search-task/', views.search_task, name='search-task'),
    path('search-projects-list/', views.search_projects_list, name='search-projects-list'),
    path('sort-projects-by-status', views.sort_projects_by_status, name='sort-projects-by-status'),
    path('get-projects', views.get_projects, name="get-projects"),
    path('get-project-stages', views.get_project_stages, name="get-project-stages"),
    path('get-tasks/<int:projectid>/', views.get_tasks, name="get-tasks"),
    path('update-task-status', views.update_task_status, name='update-task-status'),
    path('profile', views.profile, name='profile'),
    path('edit-profile', views.edit_profile, name='edit-profile'),
    path('assign-task', views.assign_task, name='assign-task'),
    path('view-project', views.view_project, name='view-project'),
    path('get-tasks-list', views.get_tasks_list, name='get-tasks-list'),
    path('get-project-tasks', views.get_project_tasks, name='get-project-tasks'),
    path('add-task-pull-request', views.add_task_pull_request, name='add-task-pull-request'),
    path('add-task-correction', views.add_task_correction, name='add-task-correction'),
    path('hold-task', views.hold_task, name='hold-task'),
    path('task-detail/', views.task_detail, name='task-detail'),
    path('sort-tasks-by-status', views.sort_tasks_by_status, name='sort-tasks-by-status'),
    path('delete-task', views.delete_task, name='delete-task'),
    path('remove-assigned-peer', views.remove_assigned_peer, name='remove-assigned-peer'),
    path('change-project-status', views.change_project_status, name='change-project-status'),
    path('update-task', views.update_task, name='update-task'),
    
    path('test', views.test, name='test'),
]