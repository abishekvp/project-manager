from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='administer'),
    path('add-vendor', views.add_vendor, name='add-vendor'),
    path('get-vendors', views.get_vendors, name='get-vendors'),
    path('disable-vendor', views.disable_vendor, name='disable-vendor'),
    path('enable-vendor', views.enable_vendor, name='enable-vendor'),
    path('delete-vendor', views.delete_vendor, name='delete-vendor'),

    path('get-vendor-password', views.get_vendor_password, name='get-vendor-password'),
    path('get-vendor-token', views.get_vendor_token, name='get-vendor-token'),
    path('change-vendor-password', views.change_vendor_password, name='change-vendor-password'),
]
