import time
import re
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
import logging
from django.http import HttpResponseForbidden
from .models import IPAddress
from django.utils.timezone import now, timedelta

MAX_REQUESTS = 1  # Maximum requests allowed
BLOCK_DURATION = 5  # Block duration in minutes

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



class RestrictIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only apply restriction for paths starting with '/api/'
        if request.path.startswith('/api/'):
            client_ip = self.get_client_ip(request)

            # Get or create IP entry in the database
            ip_entry, created = IPAddress.objects.get_or_create(ip=client_ip)

            # Check if the IP is blocked
            if ip_entry.is_blocked():
                return HttpResponseForbidden("Too many requests. Please try again later.")

            # Update request count
            ip_entry.request_count += 1

            # Restrict if the max requests are exceeded
            if ip_entry.request_count > MAX_REQUESTS:
                ip_entry.blocked_until = now() + timedelta(minutes=BLOCK_DURATION)
                ip_entry.save()
                return HttpResponseForbidden("Too many requests. Please try again later.")

            # Save the IP entry
            ip_entry.save()

        # Proceed with the request
        response = self.get_response(request)
        return response

    @staticmethod
    def get_client_ip(request):
        """Extracts the client's IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip