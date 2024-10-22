from django.urls import path
from . import views

urlpatterns = [
    path('', views.index,name="index"),
    path('signup', views.signup,name="signup"),
    path('signin/', views.signin,name="signin"),
    path('signout/', views.signout,name="signout"),
    path('search-users/', views.search_users, name='search_users'),
    path('get-peers', views.get_peers, name="get-peers"),
    path('get-projects', views.get_projects, name="get-projects"),
    path('get-tasks/<int:projectid>/', views.get_tasks, name="get-tasks"),
    path('update-task-status', views.update_task_status, name='update-task-status'),
    path('profile', views.profile, name='profile'),
    path('edit-profile', views.edit_profile, name='edit-profile'),
    path('assign-task', views.assign_task, name='assign-task'),
    path('view-project', views.view_project, name='view-project'),
    path('get-task-list', views.get_task_list, name='get-task-list'),
    path('task-detail/', views.task_detail, name='task-detail'),
    path('sort-tasks-by-status/<str:status>/', views.sort_tasks_by_status, name='sort-tasks-by-status'),
]