from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('message', csrf_exempt(views.messsage), name='messsage'),
]
