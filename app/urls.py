from django.urls import path
from . import views, api_views, rest_api

urlpatterns = [

    path('', views.index,name="index"),
    path('access-restricted', views.access_restricted, name='access-restricted'),
    path('signup', views.signup,name="signup"),
    path('signin/', views.signin,name="signin"),
    path('signout/', views.signout,name="signout"),
    path('verify-2fa-login', views.verify_2fa_login, name='verify_2fa_login'),
    path('forgot-password', views.forgot_password, name='forgot_password'),
    path('verify-otp', views.verify_otp, name='verify_otp'),
    path('reset-password', views.reset_password, name='reset_password'),
    path('enable-2fa', views.enable_two_factor_auth, name='enable_2fa'),
    path('disable-2fa', views.disable_two_factor_auth, name='disable_2fa'),
    path('2fa-backup-codes', views.two_factor_backup_codes, name='profile_2fa_backup_codes'),
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

    # AJAX API Endpoints
    path('api/tasks/', api_views.api_get_tasks, name='api-get-tasks'),
    path('api/projects/', api_views.api_get_projects, name='api-get-projects'),
    path('api/tasks/update-status/', api_views.api_update_task_status, name='api-update-task-status'),
    path('api/tasks/log-time/', api_views.api_log_task_time, name='api-log-task-time'),
    path('api/tasks/update-priority/', api_views.api_update_task_priority, name='api-update-task-priority'),
    path('api/dashboard/stats/', api_views.api_get_dashboard_stats, name='api-dashboard-stats'),
    path('api/kanban/', api_views.api_get_kanban_data, name='api-kanban-data'),

    # Real-time Features API
    # Notifications
    path('api/notifications/', rest_api.api_get_notifications, name='api-get-notifications'),
    path('api/notifications/mark-read/', rest_api.api_mark_notification_read, name='api-mark-notification-read'),
    path('api/notifications/mark-all-read/', rest_api.api_mark_all_notifications_read, name='api-mark-all-read'),
    path('api/notifications/unread-count/', rest_api.api_get_unread_notification_count, name='api-unread-count'),

    # Task Comments
    path('api/tasks/<int:task_id>/comments/', rest_api.api_get_task_comments, name='api-get-comments'),
    path('api/tasks/<int:task_id>/comments/create/', rest_api.api_create_task_comment, name='api-create-comment'),
    path('api/comments/<int:comment_id>/delete/', rest_api.api_delete_task_comment, name='api-delete-comment'),

    # File Attachments
    path('api/tasks/<int:task_id>/attachments/', rest_api.api_get_task_attachments, name='api-get-attachments'),
    path('api/tasks/<int:task_id>/attachments/upload/', rest_api.api_upload_task_attachment, name='api-upload-attachment'),
    path('api/attachments/<int:attachment_id>/download/', rest_api.api_download_attachment, name='api-download-attachment'),
    path('api/attachments/<int:attachment_id>/delete/', rest_api.api_delete_attachment, name='api-delete-attachment'),

    # Activity Feed
    path('api/activity-feed/', rest_api.api_get_activity_feed, name='api-activity-feed'),

    # Team Collaboration
    path('api/tasks/<int:task_id>/watch/', rest_api.api_watch_task, name='api-watch-task'),
    path('api/tasks/<int:task_id>/unwatch/', rest_api.api_unwatch_task, name='api-unwatch-task'),
    path('api/tasks/<int:task_id>/watchers/', rest_api.api_get_task_watchers, name='api-get-watchers'),

    # Dashboard Analytics
    path('api/dashboard/analytics/', rest_api.api_get_dashboard_analytics, name='api-dashboard-analytics'),
]