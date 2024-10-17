import logging
from django.shortcuts import render

logger = logging.getLogger(__name__)

class Handle500Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        logger.error(f'An error occurred: {exception}', exc_info=True)
        return render(request, '500.html', status=500)

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
