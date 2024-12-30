from django.shortcuts import render
from django.http import JsonResponse
from .models import Messages

# Create your views here.
def messsage(request):
    from api.models import TokenUser
    name = request.POST.get('name')
    email = request.POST.get('email')
    message = request.POST.get('message')
    contact = request.POST.get('contact')
    token = request.POST.get('token')
    user = None
    if token:
        user = TokenUser.objects.filter(token=token).first().user
    if user:
        Messages.objects.create(
            name=name.strip(),
            email=email.strip(),
            message=message.strip(),
            contact=contact.strip(),
            user=user
        )
        return JsonResponse({'status_code': 200, 'message': 'Message sent successfully'})
    else:
        return JsonResponse({'status_code': 401, 'message': 'Unauthorized'})