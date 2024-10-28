from django.http import HttpResponseForbidden
from django_user_agents.utils import get_user_agent
from django.shortcuts import render, redirect
import logging

logger = logging.getLogger(__name__)

class Handle500Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        logger.error(f'An error occurred: {exception}', exc_info=True)
        return redirect('index')

logger = logging.getLogger('django.request')

class LogErrorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Log 404 errors
        if response.status_code == 404:
            logger.error(f"404 Not Found: {request.path}")
        
        # Log 403 errors
        elif response.status_code == 403:
            logger.error(f"403 Forbidden: {request.path}")

        # Log 500 errors
        elif response.status_code == 500:
            logger.error(f"500 Internal Server Error: {request.path}")

        return response

class RestrictMobileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_agent = get_user_agent(request)
        screen_width = request.headers.get('X-Screen-Width')
        screen_height = request.headers.get('X-Screen-Height')

        # Mobile-like screen resolution (e.g., width less than 800px)
        if user_agent.is_mobile or (screen_width and int(screen_width) < 800):
            return render(request, "access_restricted.html")
        
        return self.get_response(request)
