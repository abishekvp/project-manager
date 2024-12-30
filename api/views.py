from django.shortcuts import render
from django.http import JsonResponse
from .models import Messages

# Create your views here.
def messsage(request):
    name = request.POST.get('name')
    email = request.POST.get('email')
    message = request.POST.get('message')
    contact = request.POST.get('contact')

    Messages.objects.create(
        name=name.strip(),
        email=email.strip(),
        message=message.strip(),
        contact=contact.strip()
    )
    
    return JsonResponse({'status_code': 200, 'message': 'Message sent successfully'})