from accounts.models import Module

def get_modules_count():
    try:
        return Module.objects.count()
    except:
        return 0
