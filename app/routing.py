"""
WebSocket URL routing configuration for Django Channels.
Maps WebSocket endpoints to their corresponding consumers.
"""
from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = [
    # Real-time notifications for logged-in user
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi(), name='notifications'),

    # Activity feed for specific project
    re_path(r'ws/activity/project/(?P<project_id>\d+)/$', consumers.ActivityFeedConsumer.as_asgi()),

    # Activity feed for specific task
    re_path(r'ws/activity/task/(?P<task_id>\d+)/$', consumers.ActivityFeedConsumer.as_asgi()),

    # Task comments/chat updates
    re_path(r'ws/task/(?P<task_id>\d+)/comments/$', consumers.ChatConsumer.as_asgi()),
]
