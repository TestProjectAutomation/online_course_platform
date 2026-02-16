# =========================
# core/views.py - فيوهات الموقع الأساسية
# =========================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.utils import timezone
from django.conf import settings

from .models import (
    SiteSettings, ContactMessage, NewsletterSubscriber,
    Testimonial, Partner, FAQ, Page, SiteFeature
)
from .forms import ContactForm, NewsletterForm, SubscriberForm, TestimonialForm, PageForm

# ==================== تعريف كلاسات CSS ====================
TAILWIND_INPUT = "w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition"
TAILWIND_TEXTAREA = "w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition resize-y"
TAILWIND_SELECT = "w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition"
TAILWIND_CHECKBOX = "w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"

# ==================== دوال مساعدة ====================

def get_site_stats():
    """الحصول على إحصائيات الموقع"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # محاولة استيراد موديلات courses إذا كانت موجودة
    try:
        from courses.models import Course, Lesson, Review
        stats = {
            'students_count': User.objects.filter(role='user').count(),
            'courses_count': Course.objects.filter(is_active=True).count(),
            'instructors_count': User.objects.filter(role='instructor').count(),
            'lessons_count': Lesson.objects.count(),
            'reviews_count': Review.objects.count(),
            'avg_rating': Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0,
        }
    except (ImportError, ModuleNotFoundError):
        # إذا لم يكن تطبيق courses مثبتاً
        stats = {
            'students_count': User.objects.filter(role='user').count(),
            'courses_count': 0,
            'instructors_count': User.objects.filter(role='instructor').count(),
            'lessons_count': 0,
            'reviews_count': 0,
            'avg_rating': 0,
        }
    
    return stats

# ==================== الصفحات العامة ====================


def home_view(request):
    """
    الصفحة الرئيسية
    """
    # محاولة استيراد موديلات courses إذا كانت موجودة
    try:
        from courses.models import Course, Category, Review
        from courses.services import CourseService
        
        featured_courses = CourseService.get_featured_courses()[:6] if hasattr(CourseService, 'get_featured_courses') else Course.objects.filter(is_featured=True, is_active=True)[:6]
        latest_courses = Course.objects.filter(is_active=True).order_by('-created_at')[:8]
        categories = Category.objects.annotate(
            course_count=Count('courses', filter=Q(courses__is_active=True))
        )[:8]
        testimonials_from_courses = Review.objects.select_related('user', 'course').order_by('-rating')[:3]
    except (ImportError, ModuleNotFoundError, AttributeError):
        featured_courses = []
        latest_courses = []
        categories = []
        testimonials_from_courses = []
    
    # جلب بيانات core
    site_features = SiteFeature.objects.filter(is_active=True).order_by('order')[:8]
    testimonials = Testimonial.objects.filter(is_active=True, is_featured=True).order_by('order')[:6]
    partners = Partner.objects.filter(is_active=True).order_by('order')[:12]
    
    # دمج الشهادات من courses و core
    all_testimonials = list(testimonials_from_courses) + list(testimonials)
    all_testimonials = all_testimonials[:6]  # أخذ أول 6 فقط
    
    # إحصائيات سريعة
    stats = get_site_stats()
    
    # نموذج الاشتراك في النشرة البريدية
    from .forms import NewsletterForm
    newsletter_form = NewsletterForm()
    
    # الحصول على إعدادات الموقع (للتأكد)
    site_settings = SiteSettings.get_active_settings()
    
    context = {
        'featured_courses': featured_courses,
        'latest_courses': latest_courses,
        'categories': categories,
        'site_features': site_features,
        'testimonials': all_testimonials,
        'partners': partners,
        'stats': stats,
        'newsletter_form': newsletter_form,
        # إضافة قيم افتراضية للتأكد
        'site_settings': site_settings,
        'site_name': site_settings.site_name if site_settings else 'منصة التعلم',
        'site_description': site_settings.site_description if site_settings else 'منصة تعليمية متكاملة',
    }
    return render(request, 'core/home.html', context)



def about_view(request):
    """
    صفحة من نحن - تعرض:
    - معلومات عن المنصة
    - فريق العمل
    - إحصائيات
    - رؤية ورسالة
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # فريق العمل (المدربين)
    team_members = User.objects.filter(role='instructor', is_active=True)[:8]
    
    # إحصائيات
    stats = {
        'years_experience': 5,
        'happy_students': User.objects.filter(role='user', is_active=True).count(),
        'courses_count': get_site_stats()['courses_count'],
        'certified_instructors': User.objects.filter(role='instructor', is_active=True).count(),
    }
    
    # شركاء الموقع
    partners = Partner.objects.filter(is_active=True, is_featured=True).order_by('order')[:8]
    
    # شهادات العملاء
    testimonials = Testimonial.objects.filter(is_active=True)[:6]
    
    context = {
        'team_members': team_members,
        'stats': stats,
        'partners': partners,
        'testimonials': testimonials,
        'mission': 'تمكين المتعلمين العرب من الوصول إلى تعليم عالي الجودة',
        'vision': 'أن نكون المنصة التعليمية الرائدة في العالم العربي',
    }
    return render(request, 'core/about.html', context)


def contact_view(request):
    """
    صفحة اتصل بنا - تحتوي على:
    - نموذج الاتصال
    - معلومات التواصل
    - الخريطة
    """
    # معلومات التواصل من إعدادات الموقع
    settings = SiteSettings.get_active_settings()
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # حفظ الرسالة في قاعدة البيانات
            contact_message = ContactMessage(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data.get('phone', ''),
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message'],
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
            contact_message.save()
            
            # هنا يمكن إضافة إرسال بريد إلكتروني
            # send_contact_email(contact_message)
            
            messages.success(request, 'تم إرسال رسالتك بنجاح، سنتواصل معك قريباً')
            return redirect('core:contact')
        else:
            messages.error(request, 'حدث خطأ في البيانات المدخلة. يرجى التحقق من الحقول')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'contact_info': {
            'email': settings.site_email if settings else None,
            'phone': settings.site_phone if settings else None,
            'whatsapp': settings.site_whatsapp if settings else None,
            'address': settings.site_address if settings else None,
        },
        'social_links': {
            'facebook': settings.facebook_url if settings else None,
            'twitter': settings.twitter_url if settings else None,
            'instagram': settings.instagram_url if settings else None,
            'linkedin': settings.linkedin_url if settings else None,
            'youtube': settings.youtube_url if settings else None,
        },
        'map_location': 'القاهرة، مصر',  # يمكن جعلها من الإعدادات
    }
    return render(request, 'core/contact.html', context)


def faq_view(request):
    """
    صفحة الأسئلة الشائعة - تعرض:
    - الأسئلة المصنفة
    - إمكانية البحث
    """
    # جلب جميع الأسئلة النشطة
    faqs = FAQ.objects.filter(is_active=True).order_by('order', 'category')
    
    # تصنيف الأسئلة
    categories = FAQ.objects.filter(is_active=True).values_list('category', flat=True).distinct()
    
    # تجميع الأسئلة حسب التصنيف
    faqs_by_category = {}
    for category_code, category_name in FAQ.category_choices:
        category_faqs = faqs.filter(category=category_code)
        if category_faqs.exists():
            faqs_by_category[category_name] = category_faqs
    
    # بحث في الأسئلة
    search_query = request.GET.get('search', '')
    if search_query:
        faqs = faqs.filter(
            Q(question__icontains=search_query) |
            Q(answer__icontains=search_query)
        )
        faqs_by_category = {'نتائج البحث': faqs}
    
    context = {
        'faqs_by_category': faqs_by_category,
        'total_faqs': faqs.count(),
        'search_query': search_query,
        'popular_faqs': faqs.filter(is_featured=True)[:5],
    }
    return render(request, 'core/faq.html', context)


def page_detail_view(request, slug):
    """
    عرض صفحة ثابتة (من نحن، سياسة الخصوصية، الشروط...)
    """
    page = get_object_or_404(Page, slug=slug, is_active=True, is_published=True)
    
    # زيادة عدد المشاهدات
    page.increment_views()
    
    # تعيين الصفحة الحالية للـ context processor
    request.current_page = page
    
    # صفحات ذات صلة
    related_pages = Page.objects.filter(
        is_active=True, 
        is_published=True
    ).exclude(id=page.id)[:5]
    
    context = {
        'page': page,
        'related_pages': related_pages,
    }
    return render(request, 'core/page_detail.html', context)


def search_view(request):
    """
    صفحة البحث المتقدم
    """
    search_query = request.GET.get('q', '')
    results = []
    total_results = 0
    
    if search_query:
        # البحث في الصفحات
        pages = Page.objects.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query),
            is_active=True,
            is_published=True
        )
        
        # البحث في الأسئلة الشائعة
        faqs = FAQ.objects.filter(
            Q(question__icontains=search_query) |
            Q(answer__icontains=search_query),
            is_active=True
        )
        
        # البحث في الدورات (إذا كان تطبيق courses مثبتاً)
        try:
            from courses.models import Course
            courses = Course.objects.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(short_description__icontains=search_query),
                is_active=True
            )[:10]
        except (ImportError, ModuleNotFoundError):
            courses = []
        
        # تجميع النتائج
        results = {
            'pages': pages,
            'faqs': faqs,
            'courses': courses,
        }
        
        total_results = pages.count() + faqs.count() + len(courses)
    
    context = {
        'search_query': search_query,
        'results': results,
        'total_results': total_results,
    }
    return render(request, 'core/search.html', context)

# ==================== نماذج الاشتراك ====================

@require_POST
def newsletter_subscribe(request):
    """
    الاشتراك في النشرة البريدية
    """
    form = NewsletterForm(request.POST)
    
    if form.is_valid():
        email = form.cleaned_data['email']
        name = form.cleaned_data.get('name', '')
        
        # إنشاء أو تحديث المشترك
        subscriber, created = NewsletterSubscriber.objects.update_or_create(
            email=email,
            defaults={
                'name': name,
                'ip_address': request.META.get('REMOTE_ADDR'),
            }
        )
        
        if created:
            messages.success(request, 'تم الاشتراك في النشرة البريدية بنجاح')
        else:
            if not subscriber.is_active:
                subscriber.is_active = True
                subscriber.save()
                messages.success(request, 'تم إعادة تفعيل اشتراكك في النشرة البريدية')
            else:
                messages.info(request, 'أنت مشترك بالفعل في النشرة البريدية')
        
        # إرسال بريد التأكيد إذا لم يتم التوثيق
        if not subscriber.is_verified:
            # send_verification_email(subscriber)
            messages.info(request, 'تم إرسال رابط التوثيق إلى بريدك الإلكتروني')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f'{error}')
    
    # العودة إلى الصفحة السابقة
    return redirect(request.META.get('HTTP_REFERER', 'core:home'))


def newsletter_unsubscribe(request, token):
    """
    إلغاء الاشتراك من النشرة البريدية
    """
    try:
        subscriber = NewsletterSubscriber.objects.get(verification_token=token)
        subscriber.unsubscribe()
        messages.success(request, 'تم إلغاء اشتراكك من النشرة البريدية بنجاح')
    except NewsletterSubscriber.DoesNotExist:
        messages.error(request, 'رابط إلغاء الاشتراك غير صالح')
    
    return redirect('core:home')


def verify_newsletter(request, token):
    """
    توثيق الاشتراك في النشرة البريدية
    """
    try:
        subscriber = NewsletterSubscriber.objects.get(verification_token=token)
        subscriber.verify()
        messages.success(request, 'تم توثيق بريدك الإلكتروني بنجاح')
    except NewsletterSubscriber.DoesNotExist:
        messages.error(request, 'رابط التوثيق غير صالح')
    
    return redirect('core:home')

# ==================== نماذج إضافية ====================

@require_POST
def submit_testimonial(request):
    """
    إرسال شهادة عميل جديدة
    """
    if request.user.is_authenticated:
        # يمكن للمستخدمين المسجلين إرسال شهادات
        name = request.user.get_full_name() or request.user.username
        email = request.user.email
    else:
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
    
    content = request.POST.get('content', '')
    rating = request.POST.get('rating', 5)
    
    if name and email and content:
        testimonial = Testimonial(
            name=name,
            position=request.POST.get('position', ''),
            company=request.POST.get('company', ''),
            content=content,
            rating=rating,
            is_active=False,  # تحتاج موافقة المشرف
        )
        
        if 'avatar' in request.FILES:
            testimonial.avatar = request.FILES['avatar']
        
        testimonial.save()
        messages.success(request, 'تم إرسال شهادتك بنجاح، بانتظار المراجعة')
    else:
        messages.error(request, 'يرجى ملء جميع الحقول المطلوبة')
    
    return redirect(request.META.get('HTTP_REFERER', 'core:home'))


def contact_api(request):
    """
    API لاستقبال رسائل الاتصال (للنماذج AJAX)
    """
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = ContactForm(request.POST)
        if form.is_valid():
            # حفظ الرسالة
            contact_message = ContactMessage(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data.get('phone', ''),
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message'],
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
            contact_message.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'تم إرسال رسالتك بنجاح'
            })
        else:
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = error_list[0]
            
            return JsonResponse({
                'status': 'error',
                'errors': errors
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def newsletter_api(request):
    """
    API للاشتراك في النشرة البريدية (للنماذج AJAX)
    """
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            name = form.cleaned_data.get('name', '')
            
            subscriber, created = NewsletterSubscriber.objects.update_or_create(
                email=email,
                defaults={
                    'name': name,
                    'ip_address': request.META.get('REMOTE_ADDR'),
                }
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'تم الاشتراك بنجاح',
                'is_new': created
            })
        else:
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = error_list[0]
            
            return JsonResponse({
                'status': 'error',
                'errors': errors
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# ==================== معالجات الأخطاء ====================

def handler404(request, exception):
    """صفحة خطأ 404 - الصفحة غير موجودة"""
    return render(request, 'core/errors/404.html', status=404)


def handler500(request):
    """صفحة خطأ 500 - خطأ في الخادم"""
    return render(request, 'core/errors/500.html', status=500)


def handler403(request, exception):
    """صفحة خطأ 403 - غير مصرح بالوصول"""
    return render(request, 'core/errors/403.html', status=403)


def handler400(request, exception):
    """صفحة خطأ 400 - طلب غير صالح"""
    return render(request, 'core/errors/400.html', status=400)


def csrf_failure(request, reason=""):
    """صفحة خطأ CSRF"""
    return render(request, 'core/errors/csrf.html', {'reason': reason}, status=403)