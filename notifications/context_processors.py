from .models import *
from django.db.models import Count



def notifications_processor(request):
    """
    Context processor للإشعارات - يجعل عدد الإشعارات متاحاً في جميع القوالب
    """
    context = {
        'notifications_count': 0,
        'unread_notifications_count': 0,
        'latest_notifications': [],
    }
    
    if request.user.is_authenticated:
        from .models import Notification
        context['unread_notifications_count'] = Notification.get_unread_count(request.user)
        context['notifications_count'] = Notification.objects.filter(user=request.user).count()
        context['latest_notifications'] = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
    
    return context