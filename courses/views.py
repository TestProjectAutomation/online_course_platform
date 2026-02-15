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
from .models import (
    Course, Category, User, Enrollment, Review, 
    Favorite, CourseModule, Lesson, LessonProgress
)
from .services import (
    CourseService, EnrollmentService, FavoriteService, 
    ReviewService, ModuleService, LessonService
)
from .forms import (
    CourseForm, CategoryForm, CourseModuleForm, LessonForm,
    ReviewForm, UserRegistrationForm, UserProfileForm,
    EnrollmentForm, LoginForm, SearchForm, ContactForm
)

# ==================== Mixins ====================

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin_user()

class InstructorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_instructor() or self.request.user.is_admin_user()
        )

# ==================== Public Views ====================

def home_view(request):
    """الصفحة الرئيسية"""
    featured_courses = CourseService.get_featured_courses()[:6]
    latest_courses = CourseService.get_latest_courses()[:8]
    categories = Category.objects.annotate(
        course_count=Count('courses', filter=Q(courses__is_active=True))
    )[:8]
    
    # إحصائيات سريعة
    stats = {
        'students_count': User.objects.filter(role='user').count(),
        'courses_count': Course.objects.filter(is_active=True).count(),
        'instructors_count': User.objects.filter(role='instructor').count(),
        'lessons_count': Lesson.objects.count(),
    }
    
    context = {
        'featured_courses': featured_courses,
        'latest_courses': latest_courses,
        'categories': categories,
        'stats': stats,
        'testimonials': Review.objects.select_related('user', 'course').order_by('-rating')[:3],
    }
    return render(request, 'home.html', context)

def about_view(request):
    """صفحة من نحن"""
    context = {
        'team_members': User.objects.filter(role='instructor').select_related('user')[:4],
        'stats': {
            'years_experience': 5,
            'happy_students': User.objects.filter(role='user').count(),
            'courses_count': Course.objects.filter(is_active=True).count(),
            'certified_instructors': User.objects.filter(role='instructor').count(),
        }
    }
    return render(request, 'about.html', context)

def contact_view(request):
    """صفحة اتصل بنا"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # هنا يمكن إرسال البريد الإلكتروني أو حفظ الرسالة
            messages.success(request, 'تم إرسال رسالتك بنجاح، سنتواصل معك قريباً')
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})

def faq_view(request):
    """صفحة الأسئلة الشائعة"""
    faqs = [
        {'question': 'كيف يمكنني التسجيل في دورة؟', 'answer': 'يمكنك التسجيل بعد إنشاء حساب وتفعيله...'},
        {'question': 'هل الشهادات معتمدة؟', 'answer': 'نعم، جميع الشهادات صادرة عن المنصة ومعتمدة...'},
        # أضف المزيد من الأسئلة
    ]
    return render(request, 'faq.html', {'faqs': faqs})

# ==================== Course Views ====================

class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = CourseService.get_active_courses()
        
        # البحث
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(instructor__username__icontains=search)
            )
        
        # تصفية حسب التصنيف
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # تصفية حسب المستوى
        level = self.request.GET.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        # تصفية حسب السعر
        price_min = self.request.GET.get('price_min')
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        
        price_max = self.request.GET.get('price_max')
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
        
        # تصفية حسب التقييم
        rating = self.request.GET.get('rating')
        if rating:
            queryset = queryset.filter(rating__gte=rating)
        
        # الترتيب
        sort = self.request.GET.get('sort', '-created_at')
        if sort in ['title', '-title', 'price', '-price', 'rating', '-rating', 'created_at', '-created_at']:
            queryset = queryset.order_by(sort)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # إحصائيات البحث
        context['total_courses'] = Course.objects.filter(is_active=True).count()
        context['categories'] = Category.objects.annotate(
            course_count=Count('courses', filter=Q(courses__is_active=True))
        )
        context['levels'] = Course.LEVEL_CHOICES
        context['search_form'] = SearchForm(self.request.GET)
        
        # حفظ معايير البحث
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'category': self.request.GET.get('category', ''),
            'level': self.request.GET.get('level', ''),
            'price_min': self.request.GET.get('price_min', ''),
            'price_max': self.request.GET.get('price_max', ''),
            'rating': self.request.GET.get('rating', ''),
            'sort': self.request.GET.get('sort', '-created_at'),
        }
        
        return context

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    slug_field = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        
        # زيادة عدد المشاهدات
        course.views_count += 1
        course.save(update_fields=['views_count'])
        
        # بيانات المستخدم إذا كان مسجل الدخول
        if self.request.user.is_authenticated:
            context['is_favorite'] = FavoriteService.is_favorite(self.request.user, course)
            context['is_enrolled'] = EnrollmentService.is_enrolled(self.request.user, course)
            context['user_review'] = ReviewService.get_user_review(self.request.user, course)
            
            if context['is_enrolled']:
                enrollment = Enrollment.objects.get(user=self.request.user, course=course)
                context['enrollment'] = enrollment
                context['lesson_progress'] = LessonProgress.objects.filter(
                    enrollment=enrollment
                ).select_related('lesson')
        
        # محتوى إضافي
        context['reviews'] = ReviewService.get_course_reviews(course)
        context['review_form'] = ReviewForm()
        context['related_courses'] = CourseService.get_related_courses(course)
        context['modules'] = course.modules.prefetch_related('lessons').all()
        context['instructor_courses'] = Course.objects.filter(
            instructor=course.instructor,
            is_active=True
        ).exclude(id=course.id)[:3]
        
        # إحصائيات الدورة
        context['total_students'] = course.enrollments.filter(status='enrolled').count()
        context['total_reviews'] = course.reviews.count()
        context['total_modules'] = course.modules.count()
        context['total_lessons'] = Lesson.objects.filter(module__course=course).count()
        
        return context

@login_required
def course_learn_view(request, slug):
    """صفحة مشاهدة الدورة (للمسجلين فقط)"""
    course = get_object_or_404(Course, slug=slug, is_active=True)
    
    # التحقق من تسجيل المستخدم
    enrollment = Enrollment.objects.filter(
        user=request.user,
        course=course,
        status='enrolled'
    ).first()
    
    if not enrollment:
        messages.error(request, 'يجب التسجيل في الدورة أولاً')
        return redirect('course_detail', slug=slug)
    
    # تحديث آخر وصول
    enrollment.last_accessed = timezone.now()
    enrollment.save(update_fields=['last_accessed'])
    
    # جلب الدروس مع التقدم
    modules = course.modules.prefetch_related('lessons').all()
    lesson_progress = LessonProgress.objects.filter(enrollment=enrollment)
    
    # تحديد أول درس غير مكتمل
    first_incomplete_lesson = None
    for module in modules:
        for lesson in module.lessons.all():
            if not lesson_progress.filter(lesson=lesson, is_completed=True).exists():
                first_incomplete_lesson = lesson
                break
        if first_incomplete_lesson:
            break
    
    context = {
        'course': course,
        'enrollment': enrollment,
        'modules': modules,
        'lesson_progress': {lp.lesson_id: lp for lp in lesson_progress},
        'first_incomplete_lesson': first_incomplete_lesson,
        'total_lessons': Lesson.objects.filter(module__course=course).count(),
        'completed_lessons': lesson_progress.filter(is_completed=True).count(),
    }
    
    return render(request, 'courses/course_learn.html', context)

@login_required
def lesson_view(request, course_slug, lesson_id):
    """مشاهدة درس معين"""
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)
    
    # التحقق من الوصول (مجاني أو مسجل)
    if not lesson.is_free:
        enrollment = Enrollment.objects.filter(
            user=request.user,
            course=course,
            status='enrolled'
        ).exists()
        
        if not enrollment:
            messages.error(request, 'يجب التسجيل في الدورة لمشاهدة هذا الدرس')
            return redirect('course_detail', slug=course_slug)
    
    # تسجيل التقدم
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(
            user=request.user,
            course=course,
            status='enrolled'
        ).first()
        
        if enrollment:
            progress, created = LessonProgress.objects.get_or_create(
                enrollment=enrollment,
                lesson=lesson
            )
            
            # تحديث آخر موضع مشاهدة (إذا كان طلب AJAX)
            if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                data = json.loads(request.body)
                if 'position' in data:
                    progress.last_watched_position = data['position']
                    progress.save()
                    return JsonResponse({'status': 'success'})
    
    # الدروس السابقة والتالية
    all_lessons = list(Lesson.objects.filter(module__course=course).order_by('module__order', 'order'))
    current_index = next((i for i, l in enumerate(all_lessons) if l.id == lesson.id), -1)
    
    prev_lesson = all_lessons[current_index - 1] if current_index > 0 else None
    next_lesson = all_lessons[current_index + 1] if current_index < len(all_lessons) - 1 else None
    
    context = {
        'course': course,
        'lesson': lesson,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'all_lessons': all_lessons,
    }
    
    return render(request, 'courses/lesson.html', context)

@login_required
def mark_lesson_complete(request, lesson_id):
    """تحديد درس كمكتمل"""
    if request.method == 'POST':
        lesson = get_object_or_404(Lesson, id=lesson_id)
        enrollment = Enrollment.objects.filter(
            user=request.user,
            course=lesson.module.course,
            status='enrolled'
        ).first()
        
        if enrollment:
            progress, created = LessonProgress.objects.get_or_create(
                enrollment=enrollment,
                lesson=lesson
            )
            progress.is_completed = True
            progress.save()
            
            messages.success(request, 'تم إكمال الدرس بنجاح')
            
            # التوجيه إلى الدرس التالي
            next_lesson = Lesson.objects.filter(
                module__course=enrollment.course,
                order__gt=lesson.order
            ).first()
            
            if next_lesson:
                return redirect('lesson_view', course_slug=enrollment.course.slug, lesson_id=next_lesson.id)
    
    return redirect('course_learn', slug=lesson.module.course.slug)

# ==================== User Authentication Views ====================

def register_view(request):
    """صفحة التسجيل"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'auth/register.html', {'form': form})

@login_required
def profile_view(request):
    """صفحة الملف الشخصي"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    # إحصائيات المستخدم
    stats = {
        'enrolled_courses': Enrollment.objects.filter(user=request.user, status='enrolled').count(),
        'completed_courses': Enrollment.objects.filter(user=request.user, status='completed').count(),
        'favorite_courses': Favorite.objects.filter(user=request.user).count(),
        'reviews_written': Review.objects.filter(user=request.user).count(),
    }
    
    recent_activities = Enrollment.objects.filter(
        user=request.user
    ).select_related('course').order_by('-last_accessed')[:5]
    
    context = {
        'form': form,
        'stats': stats,
        'recent_activities': recent_activities,
    }
    return render(request, 'auth/profile.html', context)

# ==================== Dashboard Views ====================

@login_required
def user_dashboard(request):
    """لوحة تحكم المستخدم العادي"""
    enrollments = Enrollment.objects.filter(
        user=request.user
    ).select_related('course').order_by('-enrolled_at')
    
    favorites = Favorite.objects.filter(
        user=request.user
    ).select_related('course')
    
    pending_enrollments = enrollments.filter(status='pending')
    active_enrollments = enrollments.filter(status='enrolled')
    completed_enrollments = enrollments.filter(status='completed')
    
    # إحصائيات التقدم
    total_lessons = 0
    completed_lessons = 0
    for enrollment in active_enrollments:
        total_lessons += Lesson.objects.filter(module__course=enrollment.course).count()
        completed_lessons += LessonProgress.objects.filter(
            enrollment=enrollment,
            is_completed=True
        ).count()
    
    overall_progress = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
    
    context = {
        'enrollments': enrollments,
        'favorites': favorites,
        'pending_enrollments': pending_enrollments,
        'active_enrollments': active_enrollments,
        'completed_enrollments': completed_enrollments,
        'overall_progress': overall_progress,
        'recent_activity': enrollments[:5],
        'stats': {
            'total_courses': enrollments.count(),
            'in_progress': active_enrollments.count(),
            'completed': completed_enrollments.count(),
            'certificates': completed_enrollments.filter(course__has_certificate=True).count(),
        }
    }
    
    return render(request, 'dashboard/user_dashboard.html', context)

@login_required
def instructor_dashboard(request):
    """لوحة تحكم المدرب"""
    if not request.user.is_instructor() and not request.user.is_admin_user():
        messages.error(request, 'ليس لديك صلاحية الوصول إلى هذه الصفحة')
        return redirect('home')
    
    # الدورات التي يدرسها
    taught_courses = Course.objects.filter(instructor=request.user)
    
    # إحصائيات
    total_students = Enrollment.objects.filter(
        course__in=taught_courses,
        status='enrolled'
    ).values('user').distinct().count()
    
    total_revenue = sum(
        e.course.price for e in Enrollment.objects.filter(
            course__in=taught_courses,
            status='enrolled'
        )
    )
    
    avg_rating = taught_courses.aggregate(avg=Avg('rating'))['avg'] or 0
    
    # أحدث التسجيلات
    recent_enrollments = Enrollment.objects.filter(
        course__in=taught_courses
    ).select_related('user', 'course').order_by('-enrolled_at')[:10]
    
    # الطلاب النشطين
    active_students = User.objects.filter(
        enrollments__course__in=taught_courses,
        enrollments__status='enrolled'
    ).distinct()[:5]
    
    context = {
        'taught_courses': taught_courses,
        'total_courses': taught_courses.count(),
        'total_students': total_students,
        'total_revenue': total_revenue,
        'avg_rating': round(avg_rating, 1),
        'recent_enrollments': recent_enrollments,
        'active_students': active_students,
        'pending_requests': Enrollment.objects.filter(
            course__in=taught_courses,
            status='pending'
        ).count(),
    }
    
    return render(request, 'dashboard/instructor_dashboard.html', context)

@staff_member_required
def admin_dashboard(request):
    """لوحة تحكم الأدمن (كاملة وشاملة)"""
    # إحصائيات عامة
    total_users = User.objects.count()
    total_students = User.objects.filter(role='user').count()
    total_instructors = User.objects.filter(role='instructor').count()
    total_admins = User.objects.filter(role='admin').count()
    
    total_courses = Course.objects.count()
    active_courses = Course.objects.filter(is_active=True).count()
    featured_courses = Course.objects.filter(is_featured=True).count()
    
    total_enrollments = Enrollment.objects.count()
    pending_enrollments = Enrollment.objects.filter(status='pending').count()
    completed_enrollments = Enrollment.objects.filter(status='completed').count()
    
    total_reviews = Review.objects.count()
    avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0
    
    # إيرادات
    total_revenue = Enrollment.objects.filter(
        status='enrolled'
    ).aggregate(total=Sum('course__price'))['total'] or 0
    
    # آخر الأنشطة
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_courses = Course.objects.order_by('-created_at')[:5]
    recent_enrollments = Enrollment.objects.select_related('user', 'course').order_by('-enrolled_at')[:5]
    recent_reviews = Review.objects.select_related('user', 'course').order_by('-created_at')[:5]
    
    # توزيع المستويات
    level_distribution = {
        'beginner': Course.objects.filter(level='beginner').count(),
        'intermediate': Course.objects.filter(level='intermediate').count(),
        'advanced': Course.objects.filter(level='advanced').count(),
        'all': Course.objects.filter(level='all').count(),
    }
    
    # توزيع التصنيفات
    category_distribution = Category.objects.annotate(
        course_count=Count('courses')
    ).values('name', 'course_count')
    
    context = {
        # إحصائيات
        'total_users': total_users,
        'total_students': total_students,
        'total_instructors': total_instructors,
        'total_admins': total_admins,
        'total_courses': total_courses,
        'active_courses': active_courses,
        'featured_courses': featured_courses,
        'total_enrollments': total_enrollments,
        'pending_enrollments': pending_enrollments,
        'completed_enrollments': completed_enrollments,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1),
        'total_revenue': total_revenue,
        
        # بيانات الجداول
        'users': User.objects.all().order_by('-date_joined'),
        'courses': Course.objects.all().select_related('category', 'instructor'),
        'categories': Category.objects.annotate(courses_count=Count('courses')),
        'enrollments': Enrollment.objects.all().select_related('user', 'course'),
        'reviews': Review.objects.all().select_related('user', 'course'),
        
        # آخر الأنشطة
        'recent_users': recent_users,
        'recent_courses': recent_courses,
        'recent_enrollments': recent_enrollments,
        'recent_reviews': recent_reviews,
        
        # الرسوم البيانية
        'level_distribution': level_distribution,
        'category_distribution': category_distribution,
        
        # طلبات pending
        'pending_requests': pending_enrollments,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)

# ==================== Admin Management Views ====================

# ---- User Management ----

@staff_member_required
def admin_users(request):
    """إدارة المستخدمين"""
    users = User.objects.all().order_by('-date_joined')
    
    # تصفية
    role = request.GET.get('role')
    if role:
        users = users.filter(role=role)
    
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    context = {
        'users': users,
        'total_users': User.objects.count(),
        'students_count': User.objects.filter(role='user').count(),
        'instructors_count': User.objects.filter(role='instructor').count(),
        'admins_count': User.objects.filter(role='admin').count(),
    }
    return render(request, 'admin/users/list.html', context)

@staff_member_required
def admin_user_detail(request, user_id):
    """تفاصيل المستخدم"""
    user = get_object_or_404(User, id=user_id)
    
    context = {
        'user': user,
        'enrollments': Enrollment.objects.filter(user=user).select_related('course'),
        'reviews': Review.objects.filter(user=user).select_related('course'),
        'favorites': Favorite.objects.filter(user=user).select_related('course'),
    }
    return render(request, 'admin/users/detail.html', context)

@staff_member_required
def admin_user_create(request):
    """إنشاء مستخدم جديد"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'تم إنشاء المستخدم {user.username} بنجاح')
            return redirect('admin_users')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'admin/users/form.html', {'form': form, 'title': 'إنشاء مستخدم جديد'})

@staff_member_required
def admin_user_edit(request, user_id):
    """تعديل مستخدم"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'تم تحديث المستخدم {user.username} بنجاح')
            return redirect('admin_user_detail', user_id=user.id)
    else:
        form = UserProfileForm(instance=user)
    
    return render(request, 'admin/users/form.html', {
        'form': form,
        'user': user,
        'title': f'تعديل المستخدم: {user.username}'
    })

@staff_member_required
def admin_user_delete(request, user_id):
    """حذف مستخدم"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'تم حذف المستخدم {username} بنجاح')
        return redirect('admin_users')
    
    return render(request, 'admin/users/delete.html', {'user': user})

@staff_member_required
def admin_user_toggle_active(request, user_id):
    """تفعيل/تعطيل مستخدم"""
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    
    status = 'مفعل' if user.is_active else 'معطل'
    messages.success(request, f'تم {status} المستخدم {user.username}')
    return redirect('admin_user_detail', user_id=user.id)

@staff_member_required
def admin_user_change_role(request, user_id):
    """تغيير دور المستخدم"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in dict(User.USER_ROLES):
            user.role = new_role
            user.save()
            messages.success(request, f'تم تغيير دور المستخدم إلى {user.get_role_display()}')
    
    return redirect('admin_user_detail', user_id=user.id)

# ---- Course Management ----

@staff_member_required
def admin_courses(request):
    """إدارة الدورات"""
    courses = Course.objects.all().select_related('category', 'instructor').order_by('-created_at')
    
    # تصفية
    status = request.GET.get('status')
    if status == 'active':
        courses = courses.filter(is_active=True)
    elif status == 'inactive':
        courses = courses.filter(is_active=False)
    
    category = request.GET.get('category')
    if category:
        courses = courses.filter(category_id=category)
    
    instructor = request.GET.get('instructor')
    if instructor:
        courses = courses.filter(instructor_id=instructor)
    
    search = request.GET.get('search')
    if search:
        courses = courses.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    
    paginator = Paginator(courses, 20)
    page = request.GET.get('page')
    courses = paginator.get_page(page)
    
    context = {
        'courses': courses,
        'total_courses': Course.objects.count(),
        'active_courses': Course.objects.filter(is_active=True).count(),
        'categories': Category.objects.all(),
        'instructors': User.objects.filter(role='instructor'),
    }
    return render(request, 'admin/courses/list.html', context)

@staff_member_required
def admin_course_detail(request, course_id):
    """تفاصيل الدورة"""
    course = get_object_or_404(Course, id=course_id)
    
    context = {
        'course': course,
        'modules': course.modules.prefetch_related('lessons').all(),
        'enrollments': Enrollment.objects.filter(course=course).select_related('user'),
        'reviews': Review.objects.filter(course=course).select_related('user'),
        'total_students': course.enrollments.filter(status='enrolled').count(),
        'total_revenue': course.enrollments.filter(status='enrolled').count() * course.price,
    }
    return render(request, 'admin/courses/detail.html', context)

@staff_member_required
def admin_course_create(request):
    """إنشاء دورة جديدة"""
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user if request.user.is_instructor() else form.cleaned_data.get('instructor')
            course.save()
            messages.success(request, f'تم إنشاء الدورة {course.title} بنجاح')
            return redirect('admin_course_detail', course_id=course.id)
    else:
        form = CourseForm()
        if request.user.is_instructor():
            form.fields['instructor'].initial = request.user
    
    return render(request, 'admin/courses/form.html', {
        'form': form,
        'title': 'إنشاء دورة جديدة'
    })

@staff_member_required
def admin_course_edit(request, course_id):
    """تعديل دورة"""
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f'تم تحديث الدورة {course.title} بنجاح')
            return redirect('admin_course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'admin/courses/form.html', {
        'form': form,
        'course': course,
        'title': f'تعديل الدورة: {course.title}'
    })

@staff_member_required
def admin_course_delete(request, course_id):
    """حذف دورة"""
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        title = course.title
        course.delete()
        messages.success(request, f'تم حذف الدورة {title} بنجاح')
        return redirect('admin_courses')
    
    return render(request, 'admin/courses/delete.html', {'course': course})

@staff_member_required
def admin_course_toggle_active(request, course_id):
    """تفعيل/تعطيل دورة"""
    course = get_object_or_404(Course, id=course_id)
    course.is_active = not course.is_active
    course.save()
    
    status = 'مفعلة' if course.is_active else 'معطلة'
    messages.success(request, f'تم {status} الدورة {course.title}')
    return redirect('admin_course_detail', course_id=course.id)

@staff_member_required
def admin_course_toggle_featured(request, course_id):
    """تفعيل/تعطيل دورة مميزة"""
    course = get_object_or_404(Course, id=course_id)
    course.is_featured = not course.is_featured
    course.save()
    
    status = 'مميزة' if course.is_featured else 'غير مميزة'
    messages.success(request, f'أصبحت الدورة {status}')
    return redirect('admin_course_detail', course_id=course.id)

# ---- Module Management ----

@staff_member_required
def admin_module_create(request, course_id):
    """إنشاء وحدة جديدة في دورة"""
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        form = CourseModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            messages.success(request, f'تم إنشاء الوحدة {module.title} بنجاح')
            return redirect('admin_course_detail', course_id=course.id)
    else:
        form = CourseModuleForm()
    
    return render(request, 'admin/courses/module_form.html', {
        'form': form,
        'course': course,
        'title': 'إنشاء وحدة جديدة'
    })

@staff_member_required
def admin_module_edit(request, module_id):
    """تعديل وحدة"""
    module = get_object_or_404(CourseModule, id=module_id)
    
    if request.method == 'POST':
        form = CourseModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, f'تم تحديث الوحدة {module.title} بنجاح')
            return redirect('admin_course_detail', course_id=module.course.id)
    else:
        form = CourseModuleForm(instance=module)
    
    return render(request, 'admin/courses/module_form.html', {
        'form': form,
        'module': module,
        'course': module.course,
        'title': f'تعديل الوحدة: {module.title}'
    })

@staff_member_required
def admin_module_delete(request, module_id):
    """حذف وحدة"""
    module = get_object_or_404(CourseModule, id=module_id)
    course = module.course
    
    if request.method == 'POST':
        title = module.title
        module.delete()
        messages.success(request, f'تم حذف الوحدة {title} بنجاح')
        return redirect('admin_course_detail', course_id=course.id)
    
    return render(request, 'admin/courses/module_delete.html', {'module': module})

# ---- Lesson Management ----

@staff_member_required
def admin_lesson_create(request, module_id):
    """إنشاء درس جديد في وحدة"""
    module = get_object_or_404(CourseModule, id=module_id)
    
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            messages.success(request, f'تم إنشاء الدرس {lesson.title} بنجاح')
            return redirect('admin_course_detail', course_id=module.course.id)
    else:
        form = LessonForm()
    
    return render(request, 'admin/courses/lesson_form.html', {
        'form': form,
        'module': module,
        'course': module.course,
        'title': 'إنشاء درس جديد'
    })

@staff_member_required
def admin_lesson_edit(request, lesson_id):
    """تعديل درس"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, f'تم تحديث الدرس {lesson.title} بنجاح')
            return redirect('admin_course_detail', course_id=lesson.module.course.id)
    else:
        form = LessonForm(instance=lesson)
    
    return render(request, 'admin/courses/lesson_form.html', {
        'form': form,
        'lesson': lesson,
        'module': lesson.module,
        'course': lesson.module.course,
        'title': f'تعديل الدرس: {lesson.title}'
    })

@staff_member_required
def admin_lesson_delete(request, lesson_id):
    """حذف درس"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.module.course
    
    if request.method == 'POST':
        title = lesson.title
        lesson.delete()
        messages.success(request, f'تم حذف الدرس {title} بنجاح')
        return redirect('admin_course_detail', course_id=course.id)
    
    return render(request, 'admin/courses/lesson_delete.html', {'lesson': lesson})

# ---- Category Management ----

@staff_member_required
def admin_categories(request):
    """إدارة التصنيفات"""
    categories = Category.objects.annotate(
        courses_count=Count('courses')
    ).order_by('name')
    
    context = {
        'categories': categories,
        'total_categories': categories.count(),
    }
    return render(request, 'admin/categories/list.html', context)

@staff_member_required
def admin_category_create(request):
    """إنشاء تصنيف جديد"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'تم إنشاء التصنيف {category.name} بنجاح')
            return redirect('admin_categories')
    else:
        form = CategoryForm()
    
    return render(request, 'admin/categories/form.html', {
        'form': form,
        'title': 'إنشاء تصنيف جديد'
    })

@staff_member_required
def admin_category_edit(request, category_id):
    """تعديل تصنيف"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'تم تحديث التصنيف {category.name} بنجاح')
            return redirect('admin_categories')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'admin/categories/form.html', {
        'form': form,
        'category': category,
        'title': f'تعديل التصنيف: {category.name}'
    })

@staff_member_required
def admin_category_delete(request, category_id):
    """حذف تصنيف"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'تم حذف التصنيف {name} بنجاح')
        return redirect('admin_categories')
    
    return render(request, 'admin/categories/delete.html', {'category': category})

# ---- Enrollment Management ----

@staff_member_required
def admin_enrollments(request):
    """إدارة التسجيلات"""
    enrollments = Enrollment.objects.all().select_related('user', 'course').order_by('-enrolled_at')
    
    # تصفية
    status = request.GET.get('status')
    if status:
        enrollments = enrollments.filter(status=status)
    
    course = request.GET.get('course')
    if course:
        enrollments = enrollments.filter(course_id=course)
    
    search = request.GET.get('search')
    if search:
        enrollments = enrollments.filter(
            Q(user__username__icontains=search) |
            Q(course__title__icontains=search)
        )
    
    paginator = Paginator(enrollments, 20)
    page = request.GET.get('page')
    enrollments = paginator.get_page(page)
    
    context = {
        'enrollments': enrollments,
        'total_enrollments': Enrollment.objects.count(),
        'courses': Course.objects.all(),
        'status_choices': Enrollment.STATUS_CHOICES,
    }
    return render(request, 'admin/enrollments/list.html', context)

@staff_member_required
def admin_enrollment_detail(request, enrollment_id):
    """تفاصيل التسجيل"""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    context = {
        'enrollment': enrollment,
        'lesson_progress': LessonProgress.objects.filter(enrollment=enrollment).select_related('lesson'),
    }
    return render(request, 'admin/enrollments/detail.html', context)

@staff_member_required
def admin_enrollment_create(request):
    """إنشاء تسجيل جديد"""
    if request.method == 'POST':
        user_id = request.POST.get('user')
        course_id = request.POST.get('course')
        notes = request.POST.get('notes', '')
        
        user = get_object_or_404(User, id=user_id)
        course = get_object_or_404(Course, id=course_id)
        
        enrollment, created = Enrollment.objects.get_or_create(
            user=user,
            course=course,
            defaults={'notes': notes, 'status': 'enrolled'}
        )
        
        if created:
            messages.success(request, f'تم تسجيل {user.username} في {course.title}')
        else:
            messages.warning(request, f'{user.username} مسجل بالفعل في هذه الدورة')
        
        return redirect('admin_enrollments')
    
    context = {
        'users': User.objects.filter(role='user').order_by('username'),
        'courses': Course.objects.filter(is_active=True).order_by('title'),
    }
    return render(request, 'admin/enrollments/create.html', context)

@staff_member_required
def admin_enrollment_update_status(request, enrollment_id):
    """تحديث حالة التسجيل"""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Enrollment.STATUS_CHOICES):
            enrollment.status = new_status
            if new_status == 'completed' and not enrollment.completed_at:
                enrollment.completed_at = timezone.now()
            enrollment.save()
            messages.success(request, f'تم تحديث حالة التسجيل إلى {enrollment.get_status_display()}')
    
    return redirect('admin_enrollment_detail', enrollment_id=enrollment.id)

@staff_member_required
def admin_enrollment_delete(request, enrollment_id):
    """حذف تسجيل"""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    if request.method == 'POST':
        info = f"{enrollment.user.username} - {enrollment.course.title}"
        enrollment.delete()
        messages.success(request, f'تم حذف التسجيل {info} بنجاح')
        return redirect('admin_enrollments')
    
    return render(request, 'admin/enrollments/delete.html', {'enrollment': enrollment})

# ---- Review Management ----

@staff_member_required
def admin_reviews(request):
    """إدارة التقييمات"""
    reviews = Review.objects.all().select_related('user', 'course').order_by('-created_at')
    
    paginator = Paginator(reviews, 20)
    page = request.GET.get('page')
    reviews = paginator.get_page(page)
    
    context = {
        'reviews': reviews,
        'total_reviews': Review.objects.count(),
        'avg_rating': Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0,
    }
    return render(request, 'admin/reviews/list.html', context)

@staff_member_required
def admin_review_delete(request, review_id):
    """حذف تقييم"""
    review = get_object_or_404(Review, id=review_id)
    
    if request.method == 'POST':
        info = f"{review.user.username} - {review.course.title}"
        review.delete()
        messages.success(request, f'تم حذف التقييم {info} بنجاح')
        return redirect('admin_reviews')
    
    return render(request, 'admin/reviews/delete.html', {'review': review})

# ==================== Reports & Exports ====================

@staff_member_required
def admin_reports(request):
    """صفحة التقارير"""
    return render(request, 'admin/reports/index.html')

@staff_member_required
def admin_export_users(request):
    """تصدير المستخدمين إلى CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'First Name', 'Last Name', 'Role', 'Date Joined', 'Is Active'])
    
    users = User.objects.all().values_list('username', 'email', 'first_name', 'last_name', 'role', 'date_joined', 'is_active')
    for user in users:
        writer.writerow(user)
    
    return response

@staff_member_required
def admin_export_courses(request):
    """تصدير الدورات إلى CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="courses.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Title', 'Category', 'Instructor', 'Price', 'Level', 'Students', 'Rating', 'Created'])
    
    courses = Course.objects.select_related('category', 'instructor').values_list(
        'title', 'category__name', 'instructor__username', 'price', 'level', 
        'students_count', 'rating', 'created_at'
    )
    for course in courses:
        writer.writerow(course)
    
    return response

@staff_member_required
def admin_export_enrollments(request):
    """تصدير التسجيلات إلى CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="enrollments.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['User', 'Course', 'Status', 'Enrolled At', 'Progress', 'Notes'])
    
    enrollments = Enrollment.objects.select_related('user', 'course').values_list(
        'user__username', 'course__title', 'status', 'enrolled_at', 'progress', 'notes'
    )
    for enrollment in enrollments:
        writer.writerow(enrollment)
    
    return response

# ==================== API-like Views (AJAX) ====================

@login_required
def ajax_toggle_favorite(request):
    """API لتبديل حالة المفضلة"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        
        is_favorite = FavoriteService.toggle_favorite(request.user, course)
        
        return JsonResponse({
            'status': 'success',
            'is_favorite': is_favorite,
            'message': 'تمت الإضافة إلى المفضلة' if is_favorite else 'تمت الإزالة من المفضلة'
        })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def ajax_update_lesson_progress(request):
    """API لتحديث تقدم الدرس"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        lesson_id = request.POST.get('lesson_id')
        position = request.POST.get('position', 0)
        
        lesson = get_object_or_404(Lesson, id=lesson_id)
        enrollment = Enrollment.objects.filter(
            user=request.user,
            course=lesson.module.course,
            status='enrolled'
        ).first()
        
        if enrollment:
            progress, created = LessonProgress.objects.get_or_create(
                enrollment=enrollment,
                lesson=lesson
            )
            progress.last_watched_position = position
            progress.save()
            
            return JsonResponse({
                'status': 'success',
                'position': position
            })
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def ajax_get_course_stats(request, course_id):
    """API للحصول على إحصائيات الدورة"""
    course = get_object_or_404(Course, id=course_id)
    
    stats = {
        'total_students': course.enrollments.filter(status='enrolled').count(),
        'total_reviews': course.reviews.count(),
        'avg_rating': float(course.rating),
        'total_lessons': Lesson.objects.filter(module__course=course).count(),
        'total_modules': course.modules.count(),
    }
    
    return JsonResponse(stats)




# ==================== User Actions ====================

@login_required
@require_POST
def toggle_favorite(request, slug):
    """
    إضافة أو إزالة دورة من المفضلة
    """
    course = get_object_or_404(Course, slug=slug, is_active=True)
    
    # استخدام الخدمة لتبديل حالة المفضلة
    is_favorite, message = FavoriteService.toggle_favorite(request.user, course)
    
    # رسالة للمستخدم
    if is_favorite:
        messages.success(request, f'تمت إضافة دورة "{course.title}" إلى المفضلة')
    else:
        messages.success(request, f'تمت إزالة دورة "{course.title}" من المفضلة')
    
    # التحقق من نوع الطلب (AJAX أو عادي)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'is_favorite': is_favorite,
            'message': message,
            'favorites_count': FavoriteService.get_user_favorites_count(request.user)
        })
    
    # إعادة التوجيه إلى الصفحة السابقة أو صفحة الدورة
    next_url = request.META.get('HTTP_REFERER', 'courses:course_detail')
    if next_url == 'courses:course_detail':
        return redirect('courses:course_detail', slug=slug)
    return redirect(next_url)

@login_required
def add_review(request, slug):
    """
    إضافة أو تحديث تقييم لدورة
    """
    course = get_object_or_404(Course, slug=slug, is_active=True)
    
    # التحقق من أن المستخدم مسجل في الدورة
    from .services import EnrollmentService
    if not EnrollmentService.is_enrolled(request.user, course) and not request.user.is_admin_user():
        messages.error(request, 'يجب التسجيل في الدورة أولاً لتتمكن من تقييمها')
        return redirect('courses:course_detail', slug=slug)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # إنشاء أو تحديث التقييم
            review, created = ReviewService.create_review(
                user=request.user,
                course=course,
                rating=form.cleaned_data['rating'],
                comment=form.cleaned_data['comment']
            )
            
            if created:
                messages.success(request, f'تم إضافة تقييمك للدورة "{course.title}" بنجاح')
            else:
                messages.success(request, f'تم تحديث تقييمك للدورة "{course.title}" بنجاح')
            
            # التحقق من نوع الطلب (AJAX)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'تم حفظ التقييم بنجاح',
                    'review': {
                        'id': review.id,
                        'rating': review.rating,
                        'comment': review.comment,
                        'created_at': review.created_at.strftime('%Y-%m-%d %H:%M'),
                        'user': {
                            'username': review.user.username,
                            'avatar': review.user.avatar.url if review.user.avatar else None
                        }
                    },
                    'course_rating': course.rating,
                    'reviews_count': course.reviews.count()
                })
            
            return redirect('courses:course_detail', slug=slug)
        else:
            messages.error(request, 'حدث خطأ في البيانات المدخلة. يرجى التحقق من التقييم والتعليق')
    
    # إذا كان الطلب GET (عرض نموذج التقييم)
    else:
        # محاولة جلب تقييم المستخدم الحالي إن وجد
        existing_review = ReviewService.get_user_review(request.user, course)
        form = ReviewForm(instance=existing_review) if existing_review else ReviewForm()
    
    return render(request, 'courses/add_review.html', {
        'form': form,
        'course': course,
        'existing_review': existing_review if 'existing_review' in locals() else None
    })

@login_required
@require_POST
def delete_review(request, review_id):
    """
    حذف تقييم
    """
    from .services import ReviewService
    
    success = ReviewService.delete_review(review_id, request.user)
    
    if success:
        messages.success(request, 'تم حذف التقييم بنجاح')
    else:
        messages.error(request, 'لم نتمكن من حذف التقييم. يرجى المحاولة مرة أخرى')
    
    # العودة إلى الصفحة السابقة
    next_url = request.META.get('HTTP_REFERER', 'courses:home')
    return redirect(next_url)

@login_required
def edit_review(request, review_id):
    """
    تعديل تقييم
    """
    from .models import Review
    from .services import ReviewService
    
    review = get_object_or_404(Review, id=review_id, user=request.user)
    course = review.course
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث التقييم بنجاح')
            return redirect('courses:course_detail', slug=course.slug)
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'courses/edit_review.html', {
        'form': form,
        'course': course,
        'review': review
    })

@login_required
def my_favorites(request):
    """
    عرض قائمة المفضلة للمستخدم
    """
    from .services import FavoriteService
    
    favorites = FavoriteService.get_user_favorites(request.user)
    
    return render(request, 'courses/favorites.html', {
        'favorites': favorites,
        'favorites_count': favorites.count()
    })

@login_required
def my_reviews(request):
    """
    عرض قائمة تقييمات المستخدم
    """
    from .models import Review
    
    reviews = Review.objects.filter(user=request.user).select_related('course').order_by('-created_at')
    
    return render(request, 'courses/my_reviews.html', {
        'reviews': reviews
    })
    
    
        