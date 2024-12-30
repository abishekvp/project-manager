from django.contrib import admin
from .models import Messages, TokenUser

# Register your models here.
admin.site.register(Messages)
admin.site.register(TokenUser)