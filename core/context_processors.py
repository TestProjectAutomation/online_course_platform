# =========================
# context_processors.py
# =========================
from .models import (
    SiteSettings, FAQ, Page, Partner, Testimonial, 
    SiteFeature, NewsletterSubscriber, ContactMessage
)
from django.conf import settings

def site_settings(request):
    """
    Context processor لإضافة إعدادات الموقع إلى جميع القوالب
    """
    # الحصول على الإعدادات النشطة
    settings_obj = SiteSettings.get_active_settings()
    
    # الحصول على الصفحات النشطة
    pages = Page.objects.filter(is_active=True, is_published=True).order_by('order')
    
    # الحصول على الصفحات للعرض في الرأس والتذييل
    header_pages = pages.filter(show_in_header=True)
    footer_pages = pages.filter(show_in_footer=True)
    
    # الحصول على الأسئلة الشائعة المميزة
    faqs = FAQ.objects.filter(is_active=True, is_featured=True)[:6]
    
    # الحصول على الشركاء النشطين
    partners = Partner.objects.filter(is_active=True).order_by('order')[:12]
    
    # الحصول على شهادات العملاء المميزة
    testimonials = Testimonial.objects.filter(is_active=True, is_featured=True)[:6]
    
    # الحصول على ميزات الموقع النشطة
    site_features = SiteFeature.objects.filter(is_active=True).order_by('order')[:8]
    
    # التحقق من وضع الصيانة
    maintenance_mode = settings_obj.maintenance_mode if settings_obj else False
    
    return {
        # إعدادات الموقع
        'site_settings': settings_obj,
        'site_name': SiteSettings.get_site_name(),
        'site_logo': SiteSettings.get_site_logo(),
        'site_favicon': SiteSettings.get_site_favicon(),
        'site_email': settings_obj.site_email if settings_obj else None,
        'site_phone': settings_obj.site_phone if settings_obj else None,
        'site_whatsapp': settings_obj.site_whatsapp if settings_obj else None,
        'site_address': settings_obj.site_address if settings_obj else None,
        'copyright_text': settings_obj.copyright_text if settings_obj else "جميع الحقوق محفوظة",
        
        # روابط التواصل الاجتماعي
        'facebook_url': settings_obj.facebook_url if settings_obj else None,
        'twitter_url': settings_obj.twitter_url if settings_obj else None,
        'instagram_url': settings_obj.instagram_url if settings_obj else None,
        'linkedin_url': settings_obj.linkedin_url if settings_obj else None,
        'youtube_url': settings_obj.youtube_url if settings_obj else None,
        
        # الصفحات
        'pages': pages,
        'header_pages': header_pages,
        'footer_pages': footer_pages,
        
        # محتوى الموقع
        'faqs': faqs,
        'partners': partners,
        'testimonials': testimonials,
        'site_features': site_features,
        
        # إعدادات الموقع
        'maintenance_mode': maintenance_mode,
        'google_analytics_id': settings_obj.google_analytics_id if settings_obj else None,
        'meta_author': settings_obj.meta_author if settings_obj else None,
        
        # معلومات debugging (اختياري)
        'debug': settings.DEBUG,
    }


def contact_info(request):
    """
    Context processor لمعلومات التواصل
    """
    settings_obj = SiteSettings.get_active_settings()
    
    return {
        'contact_email': settings_obj.site_email if settings_obj else None,
        'contact_phone': settings_obj.site_phone if settings_obj else None,
        'contact_whatsapp': settings_obj.site_whatsapp if settings_obj else None,
        'contact_address': settings_obj.site_address if settings_obj else None,
    }


def social_links(request):
    """
    Context processor لروابط التواصل الاجتماعي
    """
    settings_obj = SiteSettings.get_active_settings()
    
    social_links = []
    
    if settings_obj:
        if settings_obj.facebook_url:
            social_links.append({
                'name': 'Facebook',
                'url': settings_obj.facebook_url,
                'icon': 'fab fa-facebook-f',
                'color': '#1877f2'
            })
        if settings_obj.twitter_url:
            social_links.append({
                'name': 'Twitter',
                'url': settings_obj.twitter_url,
                'icon': 'fab fa-twitter',
                'color': '#1da1f2'
            })
        if settings_obj.instagram_url:
            social_links.append({
                'name': 'Instagram',
                'url': settings_obj.instagram_url,
                'icon': 'fab fa-instagram',
                'color': '#e4405f'
            })
        if settings_obj.linkedin_url:
            social_links.append({
                'name': 'LinkedIn',
                'url': settings_obj.linkedin_url,
                'icon': 'fab fa-linkedin-in',
                'color': '#0077b5'
            })
        if settings_obj.youtube_url:
            social_links.append({
                'name': 'YouTube',
                'url': settings_obj.youtube_url,
                'icon': 'fab fa-youtube',
                'color': '#ff0000'
            })
    
    return {
        'social_links': social_links,
    }


def meta_tags(request):
    """
    Context processor لوسوم SEO
    """
    settings_obj = SiteSettings.get_active_settings()
    
    # تحديد عنوان الصفحة الحالية
    page_title = None
    page_description = None
    page_image = None
    
    # محاولة الحصول على عنوان الصفحة الحالية من request
    if hasattr(request, 'current_page') and request.current_page:
        page = request.current_page
        page_title = page.title
        page_description = page.meta_description or page.content[:160]
        page_image = page.featured_image.url if page.featured_image else None
    
    return {
        'meta_title': page_title or (settings_obj.site_title if settings_obj else None),
        'meta_description': page_description or (settings_obj.site_description if settings_obj else None),
        'meta_keywords': settings_obj.site_keywords if settings_obj else None,
        'meta_author': settings_obj.meta_author if settings_obj else None,
        'meta_image': page_image or (settings_obj.site_og_image.url if settings_obj and settings_obj.site_og_image else None),
        'meta_url': request.build_absolute_uri(),
    }


def breadcrumbs(request):
    """
    Context processor لفتات الخبز (breadcrumbs)
    """
    breadcrumbs = []
    
    # إضافة الصفحة الرئيسية
    breadcrumbs.append({
        'title': 'الرئيسية',
        'url': '/',
        'active': False
    })
    
    # محاولة بناء مسار التنقل بناءً على URL
    path_parts = request.path.split('/')
    current_path = ''
    
    for i, part in enumerate(path_parts):
        if part and part not in ['ar', 'en']:  # تجاهل أجزاء اللغة
            current_path += f'/{part}'
            
            # تخطي آخر جزء إذا كان هو الصفحة الحالية (سيتم إضافته لاحقاً)
            if i < len(path_parts) - 1 or not part:
                breadcrumbs.append({
                    'title': part.replace('-', ' ').title(),
                    'url': current_path,
                    'active': False
                })
    
    # تحديث آخر عنصر ليكون نشطاً
    if breadcrumbs:
        breadcrumbs[-1]['active'] = True
    
    return {
        'breadcrumbs': breadcrumbs,
    }


def notifications(request):
    """
    Context processor للإشعارات (إذا كان المستخدم مسجلاً)
    """
    notifications_data = {
        'unread_notifications_count': 0,
        'latest_notifications': [],
    }
    
    if request.user.is_authenticated:
        # إذا كان لديك نموذج إشعارات، يمكنك إضافته هنا
        # from notifications.models import Notification
        # notifications_data['unread_notifications_count'] = Notification.objects.filter(
        #     recipient=request.user, 
        #     read=False
        # ).count()
        # notifications_data['latest_notifications'] = Notification.objects.filter(
        #     recipient=request.user
        # ).order_by('-created_at')[:5]
        pass
    
    return notifications_data


def cart_info(request):
    """
    Context processor لمعلومات السلة (إذا كان الموقع تجارياً)
    """
    cart_data = {
        'cart_count': 0,
        'cart_total': 0,
        'cart_items': [],
    }
    
    # ✅ الطريقة الصحيحة: السلة هي قائمة من IDs
    cart = request.session.get('cart', [])
    
    if cart:
        cart_data['cart_count'] = len(cart)
        
        # إذا أردت جلب تفاصيل الدورات
        try:
            from courses.models import Course
            cart_items = Course.objects.filter(id__in=cart, is_active=True)
            cart_data['cart_items'] = cart_items
            cart_data['cart_total'] = sum(course.price for course in cart_items)
        except (ImportError, Exception):
            # إذا لم يكن تطبيق courses متاحاً
            pass
    
    return cart_data

def current_year(request):
    """
    Context processor للسنة الحالية
    """
    from datetime import datetime
    return {
        'current_year': datetime.now().year,
    }


def is_mobile(request):
    """
    Context processor للكشف عن أجهزة المحمول
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    mobile_agents = ['android', 'iphone', 'ipad', 'ipod', 'blackberry', 'windows phone']
    
    is_mobile = any(agent in user_agent for agent in mobile_agents)
    
    return {
        'is_mobile': is_mobile,
        'is_tablet': 'ipad' in user_agent or 'tablet' in user_agent,
    }