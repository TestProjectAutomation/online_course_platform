from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count, Avg, Sum
from django.urls import reverse_lazy
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db import transaction
import csv
import json
from django.views.decorators.http import require_POST
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.utils.timesince import timesince

from .models import *
from courses.models import *
from courses.services import *
from courses.forms import *

from .context_processors import notifications_processor






# ==================== نظام الإشعارات المتكامل ====================

@login_required
def notifications_view(request):
    """عرض جميع الإشعارات"""
    from .models import Notification
    
    # تصفية الإشعارات
    filter_type = request.GET.get('filter', 'all')
    
    notifications = Notification.objects.filter(user=request.user)
    
    if filter_type == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_type == 'important':
        notifications = notifications.filter(is_important=True)
    
    # ترقيم الصفحات
    paginator = Paginator(notifications, 20)
    page = request.GET.get('page')
    notifications = paginator.get_page(page)
    
    # إحصائيات
    total_unread = Notification.get_unread_count(request.user)
    total_notifications = Notification.objects.filter(user=request.user).count()
    
    context = {
        'notifications': notifications,
        'total_unread': total_unread,
        'total_notifications': total_notifications,
        'filter_type': filter_type,
    }
    return render(request, 'notifications/notifications.html', context)


@login_required
def notifications_count(request):
    """API للحصول على عدد الإشعارات غير المقروءة"""
    from .models import Notification
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        unread_count = Notification.get_unread_count(request.user)
        return JsonResponse({
            'status': 'success',
            'unread_count': unread_count
        })
    return JsonResponse({'status': 'error'}, status=400)


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """تحديد إشعار كمقروء"""
    from .models import Notification
    
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.mark_as_read()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'تم تحديد الإشعار كمقروء',
                'unread_count': Notification.get_unread_count(request.user)
            })
        
        messages.success(request, 'تم تحديد الإشعار كمقروء')
        return redirect('notifications:notifications')
        
    except Notification.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'الإشعار غير موجود'}, status=404)
        messages.error(request, 'الإشعار غير موجود')
        return redirect('notifications:notifications')


@login_required
@require_POST
def mark_all_notifications_read(request):
    """تحديد كل الإشعارات كمقروءة"""
    from .models import Notification
    
    Notification.mark_all_as_read(request.user)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'تم تحديد كل الإشعارات كمقروءة',
            'unread_count': 0
        })
    
    messages.success(request, 'تم تحديد كل الإشعارات كمقروءة')
    return redirect('notifications:notifications')


@login_required
@require_POST
def delete_notification(request, notification_id):
    """حذف إشعار"""
    from .models import Notification
    
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'تم حذف الإشعار',
                'unread_count': Notification.get_unread_count(request.user)
            })
        
        messages.success(request, 'تم حذف الإشعار')
        return redirect('notifications:notifications')
        
    except Notification.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'الإشعار غير موجود'}, status=404)
        messages.error(request, 'الإشعار غير موجود')
        return redirect('notifications:notifications')


# ==================== دوال مساعدة للإشعارات ====================

def create_notification(user, title, message, notification_type='info', link=None, icon=None):
    """دالة مساعدة لإنشاء الإشعارات من أي مكان في المشروع"""
    from .models import Notification
    return Notification.create_notification(user, title, message, notification_type, link, icon)


def notify_enrollment_approved(enrollment):
    """إشعار عند الموافقة على طلب تسجيل"""
    title = "✅ تم الموافقة على طلب التسجيل"
    message = f"تمت الموافقة على طلب التسجيل في دورة {enrollment.course.title}"
    link = f"/course/{enrollment.course.slug}/"
    icon = "fa-check-circle"
    create_notification(enrollment.user, title, message, 'success', link, icon)


def notify_enrollment_rejected(enrollment):
    """إشعار عند رفض طلب تسجيل"""
    title = "❌ تم رفض طلب التسجيل"
    message = f"عذراً، تم رفض طلب التسجيل في دورة {enrollment.course.title}"
    icon = "fa-times-circle"
    create_notification(enrollment.user, title, message, 'error', None, icon)


def notify_course_completed(enrollment):
    """إشعار عند إكمال دورة"""
    title = "🎉 تهانينا! لقد أكملت الدورة"
    message = f"لقد أكملت بنجاح دورة {enrollment.course.title}. يمكنك الآن تحميل الشهادة"
    link = f"/certificate/{enrollment.id}/"
    icon = "fa-graduation-cap"
    create_notification(enrollment.user, title, message, 'success', link, icon)


def notify_new_course(course):
    """إشعار للمدرب عند إضافة دورة جديدة"""
    title = "📚 دورة جديدة"
    message = f"تم إضافة دورة جديدة: {course.title}"
    link = f"/course/{course.slug}/"
    icon = "fa-book-open"
    create_notification(course.instructor, title, message, 'info', link, icon)


def notify_new_review(review):
    """إشعار للمدرب عند إضافة تقييم جديد"""
    title = "⭐ تقييم جديد"
    message = f"تم إضافة تقييم جديد على دورة {review.course.title}"
    link = f"/course/{review.course.slug}/#reviews"
    icon = "fa-star"
    create_notification(review.course.instructor, title, message, 'info', link, icon)
    
    