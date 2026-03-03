"""
WebSocket consumers for real-time notifications and activity streaming.
Uses Django Channels for handling WebSocket connections.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import TaskNotification, ActivityLog, TaskComment


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.
    Clients subscribe to notifications channel and receive updates.
    """

    async def connect(self):
        """
        Handle WebSocket connection.
        Subscribe to user-specific notification group.
        """
        user = self.scope.get('user')
        if user and user.is_authenticated:
            self.user_id = user.id
            self.user_group = f'notifications_user_{self.user_id}'

            # Join user notification group
            await self.channel_layer.group_add(self.user_group, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(self.user_group, self.channel_name)

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages.
        Clients can mark notifications as read or request notification data.
        """
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'mark_as_read':
                notification_id = data.get('notification_id')
                await self.mark_notification_read(notification_id)

            elif action == 'get_unread_count':
                count = await self.get_unread_notification_count()
                await self.send(text_data=json.dumps({
                    'type': 'unread_count',
                    'count': count
                }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))

    async def notification_created(self, event):
        """
        Handler for new notification events.
        Called when a notification is created for this user.
        """
        notification = event.get('notification')
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': notification,
            'timestamp': event.get('timestamp')
        }))

    async def activity_created(self, event):
        """
        Handler for new activity events.
        Broadcasts when task or project activity occurs.
        """
        activity = event.get('activity')
        await self.send(text_data=json.dumps({
            'type': 'activity',
            'activity': activity,
            'timestamp': event.get('timestamp')
        }))

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark notification as read."""
        try:
            notification = TaskNotification.objects.get(id=notification_id)
            notification.mark_as_read()
        except TaskNotification.DoesNotExist:
            pass

    @database_sync_to_async
    def get_unread_notification_count(self):
        """Get count of unread notifications for user."""
        return TaskNotification.objects.filter(
            user_id=self.user_id,
            is_read=False
        ).count()


class ActivityFeedConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time activity feed.
    Clients subscribe to project or task activity updates.
    """

    async def connect(self):
        """
        Handle WebSocket connection.
        Clients can subscribe to specific project/task activity.
        """
        self.user = self.scope.get('user')
        self.project_id = self.scope['url_route']['kwargs'].get('project_id')
        self.task_id = self.scope['url_route']['kwargs'].get('task_id')

        if self.user and self.user.is_authenticated:
            # Create activity group name
            if self.project_id:
                self.activity_group = f'activity_project_{self.project_id}'
            elif self.task_id:
                self.activity_group = f'activity_task_{self.task_id}'
            else:
                await self.close()
                return

            await self.channel_layer.group_add(self.activity_group, self.channel_name)
            await self.accept()

            # Send recent activities
            activities = await self.get_recent_activities()
            await self.send(text_data=json.dumps({
                'type': 'initial_activities',
                'activities': activities
            }))
        else:
            await self.close()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'activity_group'):
            await self.channel_layer.group_discard(self.activity_group, self.channel_name)

    async def activity_update(self, event):
        """
        Handler for activity updates.
        Broadcasts updates to all connected clients in the activity group.
        """
        await self.send(text_data=json.dumps({
            'type': 'activity_update',
            'activity': event.get('activity'),
            'timestamp': event.get('timestamp')
        }))

    @database_sync_to_async
    def get_recent_activities(self):
        """Get recent activities for the project or task."""
        activities = []
        if self.project_id:
            activity_logs = ActivityLog.objects.filter(
                project_id=self.project_id
            ).select_related('user', 'task', 'project')[:20]
        else:
            activity_logs = ActivityLog.objects.filter(
                task_id=self.task_id
            ).select_related('user', 'task', 'project')[:20]

        for log in reversed(activity_logs):
            activities.append({
                'id': log.id,
                'user': log.user.username,
                'action': log.action,
                'description': log.description,
                'timestamp': log.created_at.isoformat(),
                'old_value': log.old_value,
                'new_value': log.new_value,
            })

        return activities


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for task comment/chat functionality.
    Enables real-time comment updates for specific tasks.
    """

    async def connect(self):
        """
        Handle WebSocket connection for task comments.
        """
        self.user = self.scope.get('user')
        self.task_id = self.scope['url_route']['kwargs'].get('task_id')
        self.task_group = f'task_comments_{self.task_id}'

        if self.user and self.user.is_authenticated:
            await self.channel_layer.group_add(self.task_group, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        await self.channel_layer.group_discard(self.task_group, self.channel_name)

    async def receive(self, text_data):
        """
        Handle incoming comment messages.
        """
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'send_comment':
                comment_text = data.get('content', '').strip()
                if comment_text:
                    comment = await self.create_comment(comment_text)

                    # Broadcast comment to all connected clients
                    await self.channel_layer.group_send(
                        self.task_group,
                        {
                            'type': 'comment_created',
                            'comment': {
                                'id': comment['id'],
                                'author': comment['author'],
                                'content': comment['content'],
                                'timestamp': comment['timestamp'],
                                'mentions': comment['mentions']
                            }
                        }
                    )
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))

    async def comment_created(self, event):
        """Handler for new comments."""
        await self.send(text_data=json.dumps({
            'type': 'comment_created',
            'comment': event.get('comment'),
            'timestamp': event.get('timestamp')
        }))

    @database_sync_to_async
    def create_comment(self, content):
        """Create a new task comment."""
        from .models import Task

        task = Task.objects.get(id=self.task_id)
        mentions = self.extract_mentions(content)

        comment = TaskComment.objects.create(
            task=task,
            author=self.user,
            content=content
        )

        # Add mentioned users
        for username in mentions:
            try:
                mentioned_user = User.objects.get(username=username)
                comment.mentions.add(mentioned_user)

                # Create notification for mentioned user
                TaskNotification.objects.create(
                    user=mentioned_user,
                    task=task,
                    notification_type='mentioned',
                    title=f'{self.user.username} mentioned you',
                    message=f'{self.user.username} mentioned you in a comment on task: {task.name}',
                    actor=self.user
                )
            except User.DoesNotExist:
                pass

        return {
            'id': comment.id,
            'author': comment.author.username,
            'content': comment.content,
            'timestamp': comment.created_at.isoformat(),
            'mentions': [u.username for u in comment.mentions.all()]
        }

    @staticmethod
    def extract_mentions(content):
        """Extract @mentions from comment text."""
        import re
        pattern = r'@(\w+)'
        matches = re.findall(pattern, content)
        return list(set(matches))  # Remove duplicates
