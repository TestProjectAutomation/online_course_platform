from .models import *
from django.db.models import Count

def site_settings(request):
    """
    سياق عام لجميع القوالب
    """
    return {
        'SITE_NAME': 'منصة التعلم',
        'SITE_DESCRIPTION': 'منصة تعليمية متكاملة',
        'CONTACT_EMAIL': 'info@example.com',
        'CONTACT_PHONE': '+1234567890',
    }
    

def categories_processor(request):
    """
    عرض التصنيفات في جميع الصفحات
    """
    categories = Category.objects.annotate(
        course_count=Count('courses', filter=models.Q(courses__is_active=True))
    ).filter(course_count__gt=0)
    
    return {
        'nav_categories': categories[:10],  # آخر 10 تصنيفات للقائمة
        'all_categories': categories,
    }

def featured_courses_processor(request):
    """
    عرض الدورات المميزة
    """
    featured_courses = Course.objects.filter(
        is_active=True, 
        is_featured=True
    ).select_related('category', 'instructor')[:6]
    
    return {
        'featured_courses': featured_courses,
    }

def user_data_processor(request):
    """
    بيانات المستخدم الخاصة
    """
    context = {}
    
    if request.user.is_authenticated:
        # عدد المفضلة
        context['favorites_count'] = Favorite.objects.filter(user=request.user).count()
        
        # الدورات المسجل فيها
        context['enrolled_courses_count'] = Enrollment.objects.filter(
            user=request.user, 
            status='enrolled'
        ).count()
        
        # إشعارات المستخدم (يمكن تطويرها لاحقاً)
        context['notifications_count'] = 0
        
        # آخر الدورات المشاهدة
        context['recent_courses'] = Enrollment.objects.filter(
            user=request.user,
            status='enrolled'
        ).select_related('course').order_by('-last_accessed')[:3]
    
    return context

def stats_processor(request):
    """
    إحصائيات عامة
    """
    from django.db.models import Count, Avg
    
    stats = {
        'total_courses': Course.objects.filter(is_active=True).count(),
        'total_students': User.objects.filter(role='user').count(),
        'total_instructors': User.objects.filter(role='instructor').count(),
        'total_enrollments': Enrollment.objects.filter(status='enrolled').count(),
    }
    
    return {
        'site_stats': stats,
    }

def breadcrumbs_processor(request):
    """
    إضافة مسار التنقل (Breadcrumbs) للصفحات
    """
    path = request.path
    breadcrumbs = []
    
    if path == '/':
        breadcrumbs.append({'name': 'الرئيسية', 'url': '/', 'active': True})
    else:
        breadcrumbs.append({'name': 'الرئيسية', 'url': '/'})
        
        # إضافة مسار التنقل حسب الصفحة
        if '/courses/' in path:
            if path == '/courses/':
                breadcrumbs.append({'name': 'الدورات', 'url': '/courses/', 'active': True})
            else:
                breadcrumbs.append({'name': 'الدورات', 'url': '/courses/'})
                
        elif '/profile/' in path:
            if request.user.is_authenticated:
                breadcrumbs.append({'name': 'الملف الشخصي', 'url': '/profile/', 'active': True})
                
        elif '/dashboard/' in path:
            if request.user.is_authenticated and (request.user.is_admin_user() or request.user.is_instructor()):
                breadcrumbs.append({'name': 'لوحة التحكم', 'url': '/dashboard/', 'active': True})
    
    return {
        'breadcrumbs': breadcrumbs
    }

def cart_processor(request):
    """
    معالج سياق السلة الخاص بتطبيق courses
    """
    cart = request.session.get('cart', [])
    cart_count = len(cart)
    
    cart_items = []
    cart_total = 0
    
    if cart:
        from .models import Course
        cart_items = Course.objects.filter(id__in=cart, is_active=True)
        cart_total = sum(course.price for course in cart_items)
    
    return {
        'cart_count': cart_count,
        'cart_items': cart_items,
        'cart_total': cart_total,
    }

# def cart_processor(request):
#     """
#     معالج سياق السلة - يجعل cart_count متاحاً في جميع القوالب
#     """
#     cart = request.session.get('cart', [])
#     cart_count = len(cart)
    
#     # اختياري: جلب تفاصيل الدورات في السلة
#     cart_items = Course.objects.filter(id__in=cart, is_active=True) if cart else []
#     cart_total = sum(course.price for course in cart_items)
    
#     return {
#         'cart_count': cart_count,
#         'cart_items': cart_items,
#         'cart_total': cart_total,
#     }

