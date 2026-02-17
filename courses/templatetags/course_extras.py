from django import template
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.text import slugify
import re  # ⚠️ أضف هذا السطر المهم

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
    """
    الحصول على قيمة من قاموس باستخدام مفتاح
    """
    if dictionary is None:
        return 0
    
    # إذا كان key عدد صحيح، نحوله إلى نص لأن القاموس قد يكون مفاتيحه نصوص
    try:
        return dictionary.get(str(key), 0)
    except (AttributeError, TypeError):
        try:
            return dictionary.get(key, 0)
        except (AttributeError, TypeError):
            return 0






@register.filter
def multiply(value, arg):
    """ضرب رقمين"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """قسمة رقمين (نسخة واحدة فقط)"""
    try:
        if arg and float(arg) != 0:
            return float(value) / float(arg)
        return 0
    except (ValueError, ZeroDivisionError, TypeError):
        return 0

@register.simple_tag
def course_progress(user, course):
    """الحصول على تقدم المستخدم في دورة"""
    try:
        from ..models import Enrollment  # استيراد داخل الدالة لتجنب circular import
        enrollment = Enrollment.objects.get(user=user, course=course)
        return enrollment.progress
    except:
        return 0

@register.inclusion_tag('courses/partials/course_card.html', takes_context=True)
def render_course_card(context, course):
    """عرض بطاقة دورة"""
    user = context.get('user')
    try:
        from ..services import FavoriteService
        is_favorite = FavoriteService.is_favorite(user, course) if user and user.is_authenticated else False
    except:
        is_favorite = False
    
    return {
        'course': course,
        'user': user,
        'is_favorite': is_favorite,
        'request': context.get('request'),
    }

@register.filter
def youtube_embed_id(url):
    """
    استخراج معرف الفيديو من رابط يوتيوب
    يدعم جميع صيغ الروابط
    """
    if not url:
        return ''
    
    import re
    
    # تحويل الرابط إلى نص
    url = str(url).strip()
    
    # قائمة بجميع الأنماط الممكنة لروابط يوتيوب
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([\w-]+)',
        r'(?:youtube\.com\/watch\?.*&v=)([\w-]+)',
        r'(?:youtu\.be\/)([\w-]+)',
        r'(?:youtube\.com\/embed\/)([\w-]+)',
        r'(?:youtube\.com\/v\/)([\w-]+)',
        r'(?:youtube\.com\/shorts\/)([\w-]+)',
        r'(?:youtube\.com\/live\/)([\w-]+)',
        r'(?:youtube\.com\/watch\?v%3D)([\w-]+)',  # روابط مشفرة
        r'(?:youtube\.com\/attribution_link\?.*v%3D)([\w-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            print(f"✅ تم استخراج معرف الفيديو: {video_id}")  # للتصحيح
            return video_id
    
    # إذا كان الرابط هو معرف بالفعل (عادة 11 حرف)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        print(f"✅ الرابط هو معرف مباشر: {url}")
        return url
    
    print(f"❌ لم نتمكن من استخراج معرف من الرابط: {url}")
    return ''


@register.filter
def is_valid_youtube_url(url):
    """التحقق من صحة رابط يوتيوب"""
    if not url:
        return False
    
    video_id = youtube_embed_id(url)
    return bool(video_id and len(video_id) == 11)

@register.filter
def is_valid_video_url(url):
    """التحقق من صحة رابط الفيديو"""
    if not url:
        return False
    
    # التحقق من رابط يوتيوب صالح
    video_id = youtube_embed_id(url)
    if video_id:
        return True
    
    # التحقق من رابط مباشر
    import re
    video_extensions = ['.mp4', '.webm', '.ogg', '.mov']
    url_lower = url.lower()
    if any(ext in url_lower for ext in video_extensions):
        return True
    
    return False

@register.filter
def get_youtube_thumbnail(url, size='medium'):
    """
    الحصول على رابط صورة مصغرة من رابط يوتيوب
    size: small, medium, large, maxres
    """
    video_id = youtube_embed_id(url)
    if not video_id:
        return ''
    
    sizes = {
        'small': 'default.jpg',
        'medium': 'mqdefault.jpg',
        'large': 'hqdefault.jpg',
        'maxres': 'maxresdefault.jpg',
    }
    
    thumbnail = sizes.get(size, 'mqdefault.jpg')
    return f'https://img.youtube.com/vi/{video_id}/{thumbnail}'

@register.filter
def is_youtube_url(url):
    """التحقق مما إذا كان الرابط من يوتيوب"""
    if not url:
        return False
    youtube_patterns = [
        r'youtube\.com',
        r'youtu\.be',
    ]
    for pattern in youtube_patterns:
        if re.search(pattern, str(url)):
            return True
    return False


