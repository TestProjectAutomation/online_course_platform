from django import template
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.text import slugify


register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """إضافة أو تحديث معلمات URL"""
    query = context['request'].GET.copy()
    for key, value in kwargs.items():
        query[key] = value
    return query.urlencode()

@register.filter
def timesince(value):
    """تنسيق الوقت المنقضي"""
    from django.utils.timesince import timesince as django_timesince
    from django.utils import timezone
    
    if not value:
        return ''
    
    now = timezone.now()
    try:
        delta = now - value
        if delta.days > 30:
            months = delta.days // 30
            return f'منذ {months} شهر'
        elif delta.days > 0:
            return f'منذ {delta.days} يوم'
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f'منذ {hours} ساعة'
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f'منذ {minutes} دقيقة'
        else:
            return 'الآن'
    except:
        return ''
    
    
@register.filter
def get_item(dictionary, key):
    """الحصول على قيمة من قاموس باستخدام مفتاح"""
    return dictionary.get(key) if dictionary else None

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def divide(value, arg):
    if arg:
        return value / arg
    return 0

@register.simple_tag
def course_progress(user, course):
    try:
        enrollment = Enrollment.objects.get(user=user, course=course)
        return enrollment.progress
    except Enrollment.DoesNotExist:
        return 0

@register.inclusion_tag('courses/partials/course_card.html')
def render_course_card(course, user=None):
    return {
        'course': course,
        'user': user,
        'is_favorite': FavoriteService.is_favorite(user, course) if user and user.is_authenticated else False
    }