from datetime import datetime, date

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