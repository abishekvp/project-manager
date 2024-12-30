from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
import constants.constants as const
from api.models import TokenUser
from utils.utility import generate_token

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        users = User.objects.filter(groups__name=const.VENDOR)
        return render(request, 'admin/index.html', {'users': users})
    else:
        return redirect('signin')


def add_vendor(request):
    if request.user.is_authenticated:
        from app.models import Profile
        from django.contrib.auth.models import Group
        name = request.POST.get('vendor_name')
        email = request.POST.get('vendor_email')
        phone = request.POST.get('vendor_contact')
        password = request.POST.get('vendor_password')
        if not name or not email or not phone or not password:
            return JsonResponse({'status_code': 404, 'message': 'Vendor details are required'})
        if User.objects.filter(username=name).exists():
            return JsonResponse({'status_code': 403, 'message': 'User already exists'})
        else:
            user = User.objects.create_user(username=name, email=email, password=password)
            group = Group.objects.all().filter(name=const.VENDOR).first()
            user.groups.add(group)
            Profile.objects.create(user=user, phone=phone)
            token = generate_token()
            TokenUser.objects.create(user=user, token=token)
            messages.success(request, 'User created successfully')
            return redirect('administer')
    else:
        return JsonResponse({'status_code': 403, 'error': 'Unauthorized access'})


def get_vendors(request):
    if request.user.is_authenticated:
        users = User.objects.filter(groups__name=const.VENDOR)
        vendors = []
        for user in users:
            vendors.append({
                'id': user.id,
                'name': user.username,
                'email': user.email,
                'phone': user.profile.phone,
                'status': user.is_active
            })
        return JsonResponse({'status_code': 200, 'message':'Vendors fecthed successfully', 'vendors': vendors})
    else:
        return JsonResponse({'status_code': 403, 'error': 'Unauthorized access'})


def delete_vendor(request):
    if request.user.is_authenticated:
        vendor_id = request.POST.get('vendor_id')
        if not vendor_id:
            return JsonResponse({'status_code': 404, 'message': 'User ID is required'})
        user = User.objects.filter(id=vendor_id).first()
        if not user:
            return JsonResponse({'status_code': 404, 'message': 'User not found'})
        user.delete()
        return JsonResponse({'status_code': 200, 'message': 'User deleted successfully'})
    else:
        return JsonResponse({'status_code': 403, 'error': 'Unauthorized access'})


def disable_vendor(request):
    if request.user.is_authenticated:
        vendor_id = request.POST.get('vendor_id')
        if not vendor_id:
            return JsonResponse({'status_code': 404, 'message': 'User ID is required'})
        user = User.objects.filter(id=vendor_id).first()
        if not user:
            return JsonResponse({'status_code': 404, 'message': 'User not found'})
        user.is_active = False
        user.save()
        return JsonResponse({'status_code': 200, 'message': 'User disabled successfully'})
    else:
        return JsonResponse({'status_code': 403, 'error': 'Unauthorized access'})


def enable_vendor(request):
    if request.user.is_authenticated:
        vendor_id = request.POST.get('vendor_id')
        if not vendor_id:
            return JsonResponse({'status_code': 404, 'message': 'User ID is required'})
        user = User.objects.filter(id=vendor_id).first()
        if not user:
            return JsonResponse({'status_code': 404, 'message': 'User not found'})
        user.is_active = True
        user.save()
        return JsonResponse({'status_code': 200, 'message': 'User enabled successfully'})
    else:
        return JsonResponse({'status_code': 403, 'error': 'Unauthorized access'})


def get_vendor_password(request):
    if request.user.is_authenticated:
        admin_username = request.POST.get('admin_username')
        admin_password = request.POST.get('admin_password')
        if not admin_username or not admin_password:
            messages.error(request, 'Admin credentials are required')
            return JsonResponse({'status_code': 404, 'message': 'Admin credentials are required'})
        filter_dict = {}
        if '@' and '.' in admin_username:
            filter_dict['email'] = admin_username
        else: filter_dict['username'] = admin_username
        admin = User.objects.filter(**filter_dict).first()
        if not admin.check_password(admin_password):
            messages.error(request, 'Invalid admin credentials')
            return JsonResponse({'status_code': 404, 'message': 'Invalid admin credentials'})
        return JsonResponse({'status_code': 200, 'message': 'Permission granted'})


def change_vendor_password(request):
    if request.user.is_authenticated:
        vendor_id = request.POST.get('vendor_id')
        new_password = request.POST.get('vendor_password')
        if not vendor_id or not new_password:
            messages.error(request, 'Password required')
            return JsonResponse({'status_code': 404, 'message': 'Password required'})
        user = User.objects.filter(id=vendor_id).first()
        if not user:
            messages.error(request, 'Vendor not found')
            return JsonResponse({'status_code': 404, 'message': 'Vendor not found'})
        user.set_password(new_password)
        user.save()
        messages.success(request, 'Vendor password changed successfully')
        return JsonResponse({'status_code': 200, 'message': 'Vendor password changed successfully'})
    else:
        return JsonResponse({'status_code': 403, 'error': 'Unauthorized access'})


def get_vendor_token(request):
    if request.user.is_authenticated:
        vendor_id = request.POST.get('vendor_id')
        if not vendor_id:
            messages.error(request, 'Vendor ID is required')
            return JsonResponse({'status_code': 404, 'message': 'Vendor ID is required'})
        user = User.objects.filter(id=vendor_id).first()
        if not user:
            messages.error(request, 'Vendor not found')
            return JsonResponse({'status_code': 404, 'message': 'Vendor not found'})
        token = TokenUser.objects.filter(user=user).first().token
        return JsonResponse({'status_code': 200, 'message': 'Token fetched successfully', 'token': token})
    else:
        return JsonResponse({'status_code': 403, 'error': 'Unauthorized access'})