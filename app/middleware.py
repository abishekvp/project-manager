from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
import logging
import re

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
        # User-Agent check to identify mobile devices
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        mobile_user_agents = [
            "android", "iphone", "ipod", "ipad", "blackberry", "mobile",
            "windows phone", "opera mini", "opera mobi"
        ]
        
        # Check if the User-Agent matches any mobile device identifier
        if any(re.search(mobile_agent, user_agent) for mobile_agent in mobile_user_agents):
            return render(request, 'access_restricted.html', status=403)
        
        response = self.get_response(request)
        return response
