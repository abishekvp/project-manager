from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(user):
        if user.is_authenticated:
            if bool(user.groups.filter(name__in=group_names)) or user.is_superuser:
                return True
        return False
    
    def decorator(view_function):
        @login_required
        def wrapper(request, *args, **kwargs):
            if in_groups(request.user):
                return view_function(request, *args, **kwargs)
            return redirect('/')
        return wrapper
    return decorator
