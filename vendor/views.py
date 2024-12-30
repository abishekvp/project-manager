from django.shortcuts import render

# Create your views here.
def index(request):
    from api.models import Messages
    customer_messages = Messages.objects.filter(user=request.user)
    list_messages = []
    for message in customer_messages:
        list_messages.append({
            'name': message.name,
            'email': message.email,
            'message': message.message,
            'contact': message.contact
        })
    return render(request, 'vendor/vendor.html', {'customer_messages': list_messages})