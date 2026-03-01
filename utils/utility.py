from datetime import datetime, date
from app.models import Project, Task
from constants.constants import *

def as_dict(obj):
    objdict = obj.__dict__.copy()  # Use copy to avoid modifying the original dict
    if objdict.get('_state'):
        del objdict['_state']

    for key, value in objdict.items():
        if isinstance(value, datetime) and value is not None:
            # Format DateTimeField
            objdict[key] = value.strftime('%Y-%m-%d %H:%M')
        elif isinstance(value, date) and value is not None:
            # Format DateField
            objdict[key] = value.strftime('%Y-%m-%d')
    return objdict

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def format_date(date):
    return date.strftime("%Y-%m-%d")

def project_statistics(request):
    role = request.user.profile.role
    if role == LEAD:
        projects = Project.objects.all()
        project_statistics = dict()
        for project in projects:
            tasks = Task.objects.filter(project=project)
            project_completion = 0
            total_task = 0
            todo = 0
            progress = 0
            verify = 0
            correction = 0
            hold = 0
            complete = 0
            for task in tasks:
                project_completion += TASK_SCORE[task.status]
                total_task += 1
                if task.status == TASK_HOLD:
                    hold += 1
                elif task.status == TASK_COMPLETE:
                    complete += 1
                elif task.status == TASK_TODO:
                    todo += 1
                elif task.status == TASK_CORRECTION:
                    correction += 1
                elif task.status == TASK_VERIFY:
                    verify += 1
                elif task.status == TASK_PROGRESS:
                    progress += 1
            project_statistics[project.name] = {
                'percent': str(project_completion).split('.')[0] + '%',
                'total_task': total_task,
                'todo': todo,
                'progress': progress,
                'verify': verify,
                'correction': correction,
                'hold': hold,
                'complete': complete
            }

def generate_token():
    import random
    import string
    from datetime import datetime
    timestamp = datetime.now().strftime('%f%S%H%M%Y%m%d')
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    mixed_token = ''
    for t_char, r_char in zip(timestamp, random_part):
        mixed_token += t_char + r_char
    mixed_token += timestamp[len(random_part):] + random_part[len(timestamp):]
    return mixed_token

def generate_otp():
    """Generate a random 6-digit OTP."""
    import random
    return str(random.randint(100000, 999999))

def create_otp_for_user(user, purpose, expires_in_minutes=10):
    """Create and save OTP for a user."""
    from app.models import OTP
    from django.utils import timezone
    from datetime import timedelta

    otp_code = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=expires_in_minutes)

    # Delete previous unused OTPs for this purpose
    OTP.objects.filter(user=user, purpose=purpose, is_used=False).delete()

    otp = OTP.objects.create(
        user=user,
        otp_code=otp_code,
        purpose=purpose,
        expires_at=expires_at
    )
    return otp

def verify_otp(user, otp_code, purpose):
    """Verify OTP for a user."""
    from app.models import OTP

    try:
        otp = OTP.objects.get(user=user, otp_code=otp_code, purpose=purpose)
        if otp.is_valid():
            otp.is_used = True
            otp.save()
            return True
        return False
    except OTP.DoesNotExist:
        return False