from django.db.models import Q, Count, Avg, Sum, Max, Min
from django.core.paginator import Paginator
from django.utils import timezone
from .models import (
    Course, Category, Enrollment, Favorite, Review, 
    User, CourseModule, Lesson, LessonProgress
)

class CourseService:
    """خدمات متقدمة للدورات"""
    
    @staticmethod
    def get_active_courses():
        """الحصول على جميع الدورات النشطة"""
        return Course.objects.filter(is_active=True).select_related(
            'category', 'instructor'
        ).prefetch_related('modules')
    
    @staticmethod
    def search_courses(query, filters=None):
        """بحث متقدم في الدورات مع فلترة"""
        queryset = Course.objects.filter(is_active=True)
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(short_description__icontains=query) |
                Q(instructor__username__icontains=query) |
                Q(instructor__first_name__icontains=query) |
                Q(instructor__last_name__icontains=query)
            )
        
        # تطبيق الفلاتر الإضافية
        if filters:
            if filters.get('category'):
                queryset = queryset.filter(category__slug=filters['category'])
            
            if filters.get('level'):
                queryset = queryset.filter(level=filters['level'])
            
            if filters.get('min_price'):
                queryset = queryset.filter(price__gte=filters['min_price'])
            
            if filters.get('max_price'):
                queryset = queryset.filter(price__lte=filters['max_price'])
            
            if filters.get('min_rating'):
                queryset = queryset.filter(rating__gte=filters['min_rating'])
            
            if filters.get('instructor'):
                queryset = queryset.filter(instructor_id=filters['instructor'])
        
        return queryset.distinct()
    
    @staticmethod
    def get_categories_with_counts():
        """الحصول على التصنيفات مع عدد الدورات"""
        return Category.objects.annotate(
            course_count=Count('courses', filter=Q(courses__is_active=True)),
            active_courses=Count('courses', filter=Q(courses__is_active=True))
        ).order_by('-course_count')
    
    @staticmethod
    def get_featured_courses(limit=6):
        """الحصول على الدورات المميزة"""
        return Course.objects.filter(
            is_active=True, 
            is_featured=True
        ).select_related('category', 'instructor')[:limit]
    
    @staticmethod
    def get_latest_courses(limit=8):
        """الحصول على أحدث الدورات"""
        return Course.objects.filter(
            is_active=True
        ).select_related(
            'category', 'instructor'
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_popular_courses(limit=6):
        """الحصول على الدورات الأكثر شهرة (حسب عدد الطلاب)"""
        return Course.objects.filter(
            is_active=True
        ).select_related(
            'category', 'instructor'
        ).order_by('-students_count', '-rating')[:limit]
    
    @staticmethod
    def get_top_rated_courses(limit=6):
        """الحصول على الدورات الأعلى تقييماً"""
        return Course.objects.filter(
            is_active=True,
            rating__gt=0
        ).select_related(
            'category', 'instructor'
        ).order_by('-rating', '-students_count')[:limit]
    
    @staticmethod
    def get_free_courses(limit=6):
        """الحصول على الدورات المجانية"""
        return Course.objects.filter(
            is_active=True,
            price=0
        ).select_related('category', 'instructor')[:limit]
    
    @staticmethod
    def get_courses_by_category(category_slug):
        """الحصول على دورات حسب التصنيف"""
        return Course.objects.filter(
            category__slug=category_slug, 
            is_active=True
        ).select_related('category', 'instructor')
    
    @staticmethod
    def get_course_detail(slug, user=None):
        """الحصول على تفاصيل الدورة مع معلومات إضافية"""
        course = Course.objects.filter(
            slug=slug, 
            is_active=True
        ).select_related(
            'category', 'instructor'
        ).prefetch_related(
            'modules__lessons',
            'reviews__user',
            'enrollments'
        ).first()
        
        if course and user and user.is_authenticated:
            course.user_enrolled = Enrollment.objects.filter(
                user=user, 
                course=course, 
                status='enrolled'
            ).exists()
            course.user_favorite = Favorite.objects.filter(
                user=user, 
                course=course
            ).exists()
        
        return course
    
    @staticmethod
    def get_related_courses(course, limit=4):
        """الحصول على دورات مشابهة"""
        return Course.objects.filter(
            Q(category=course.category) | Q(level=course.level),
            is_active=True
        ).exclude(id=course.id).select_related(
            'category', 'instructor'
        ).annotate(
            relevance=Count('id')
        ).order_by('-relevance', '-rating')[:limit]
    
    @staticmethod
    def get_instructor_courses(instructor_id, limit=None):
        """الحصول على دورات مدرب معين"""
        queryset = Course.objects.filter(
            instructor_id=instructor_id,
            is_active=True
        ).select_related('category').order_by('-created_at')
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    @staticmethod
    def get_course_stats(course_id):
        """الحصول على إحصائيات متقدمة للدورة"""
        course = Course.objects.get(id=course_id)
        
        stats = {
            'total_students': Enrollment.objects.filter(course=course, status='enrolled').count(),
            'completed_students': Enrollment.objects.filter(course=course, status='completed').count(),
            'pending_requests': Enrollment.objects.filter(course=course, status='pending').count(),
            'total_reviews': course.reviews.count(),
            'avg_rating': course.rating,
            'total_lessons': Lesson.objects.filter(module__course=course).count(),
            'total_modules': course.modules.count(),
            'total_duration': Lesson.objects.filter(module__course=course).aggregate(
                total=Sum('duration_minutes')
            )['total'] or 0,
            'completion_rate': 0,
        }
        
        # حساب نسبة الإكمال
        if stats['total_students'] > 0:
            stats['completion_rate'] = (stats['completed_students'] / stats['total_students']) * 100
        
        return stats
    
    @staticmethod
    def get_course_progress(user, course):
        """الحصول على تقدم المستخدم في الدورة"""
        try:
            enrollment = Enrollment.objects.get(user=user, course=course)
            total_lessons = Lesson.objects.filter(module__course=course).count()
            completed_lessons = LessonProgress.objects.filter(
                enrollment=enrollment,
                is_completed=True
            ).count()
            
            return {
                'enrollment': enrollment,
                'total_lessons': total_lessons,
                'completed_lessons': completed_lessons,
                'progress_percentage': int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0,
                'last_accessed': enrollment.last_accessed,
            }
        except Enrollment.DoesNotExist:
            return None
    
    @staticmethod
    def get_course_recommendations(user, limit=4):
        """توصيات مخصصة للمستخدم بناءً على اهتماماته"""
        if not user.is_authenticated:
            return CourseService.get_popular_courses(limit)
        
        # الحصول على تصنيفات الدورات التي سجل فيها المستخدم
        user_categories = Category.objects.filter(
            courses__enrollments__user=user,
            courses__enrollments__status='enrolled'
        ).distinct()
        
        # الحصول على مستويات الدورات التي سجل فيها المستخدم
        user_levels = Course.objects.filter(
            enrollments__user=user,
            enrollments__status='enrolled'
        ).values_list('level', flat=True).distinct()
        
        # توصيات بناءً على التصنيفات والمستويات المفضلة
        recommendations = Course.objects.filter(
            Q(category__in=user_categories) | Q(level__in=user_levels),
            is_active=True
        ).exclude(
            enrollments__user=user,
            enrollments__status__in=['enrolled', 'completed']
        ).select_related(
            'category', 'instructor'
        ).annotate(
            match_score=Count('id')
        ).order_by('-match_score', '-rating')[:limit]
        
        if recommendations.count() < limit:
            # إضافة دورات شائعة إذا لم تكن التوصيات كافية
            popular = CourseService.get_popular_courses(limit - recommendations.count())
            recommendations = list(recommendations) + list(popular)
        
        return recommendations

class EnrollmentService:
    """خدمات التسجيل في الدورات"""
    
    @staticmethod
    def get_user_enrollments(user, status=None):
        """الحصول على تسجيلات المستخدم"""
        queryset = Enrollment.objects.filter(user=user).select_related(
            'course', 'course__category', 'course__instructor'
        )
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-enrolled_at')
    
    @staticmethod
    def get_user_enrolled_courses(user):
        """الحصول على الدورات المسجل فيها المستخدم"""
        return Course.objects.filter(
            enrollments__user=user, 
            enrollments__status='enrolled'
        ).select_related('category', 'instructor')
    
    @staticmethod
    def get_user_completed_courses(user):
        """الحصول على الدورات المكتملة للمستخدم"""
        return Course.objects.filter(
            enrollments__user=user, 
            enrollments__status='completed'
        ).select_related('category', 'instructor')
    
    @staticmethod
    def get_user_pending_enrollments(user):
        """الحصول على طلبات التسجيل المعلقة"""
        return Enrollment.objects.filter(
            user=user, 
            status='pending'
        ).select_related('course')
    
    @staticmethod
    def is_enrolled(user, course):
        """التحقق مما إذا كان المستخدم مسجلاً في الدورة"""
        if not user.is_authenticated:
            return False
        return Enrollment.objects.filter(
            user=user, 
            course=course, 
            status='enrolled'
        ).exists()
    
    @staticmethod
    def create_enrollment(user, course, notes="", status='pending'):
        """إنشاء تسجيل جديد في الدورة"""
        enrollment, created = Enrollment.objects.get_or_create(
            user=user,
            course=course,
            defaults={
                'status': status,
                'notes': notes,
                'enrolled_at': timezone.now()
            }
        )
        
        if not created and enrollment.status != status:
            enrollment.status = status
            enrollment.save()
        
        # تحديث عدد الطلاب إذا كان التسجيل مباشراً
        if status == 'enrolled' and (created or enrollment.status == 'enrolled'):
            course.students_count += 1
            course.save()
        
        return enrollment, created
    
    @staticmethod
    def approve_enrollment(enrollment_id):
        """الموافقة على طلب تسجيل"""
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id, status='pending')
            enrollment.status = 'enrolled'
            enrollment.save()
            
            # تحديث عدد الطلاب
            course = enrollment.course
            course.students_count += 1
            course.save()
            
            return enrollment
        except Enrollment.DoesNotExist:
            return None
    
    @staticmethod
    def reject_enrollment(enrollment_id):
        """رفض طلب تسجيل"""
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id, status='pending')
            enrollment.status = 'cancelled'
            enrollment.save()
            return enrollment
        except Enrollment.DoesNotExist:
            return None
    
    @staticmethod
    def complete_enrollment(enrollment_id):
        """إكمال الدورة"""
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id, status='enrolled')
            enrollment.status = 'completed'
            enrollment.completed_at = timezone.now()
            enrollment.save()
            return enrollment
        except Enrollment.DoesNotExist:
            return None
    
    @staticmethod
    def get_enrollment_stats():
        """إحصائيات التسجيلات العامة"""
        total = Enrollment.objects.count()
        pending = Enrollment.objects.filter(status='pending').count()
        enrolled = Enrollment.objects.filter(status='enrolled').count()
        completed = Enrollment.objects.filter(status='completed').count()
        cancelled = Enrollment.objects.filter(status='cancelled').count()
        
        return {
            'total': total,
            'pending': pending,
            'enrolled': enrolled,
            'completed': completed,
            'cancelled': cancelled,
            'pending_percentage': (pending / total * 100) if total > 0 else 0,
            'completion_rate': (completed / enrolled * 100) if enrolled > 0 else 0,
        }

class FavoriteService:
    """خدمات المفضلة"""
    
    @staticmethod
    def get_user_favorites(user):
        """الحصول على قائمة مفضلة المستخدم"""
        return Course.objects.filter(
            favorited_by__user=user,
            is_active=True
        ).select_related('category', 'instructor')
    
    @staticmethod
    def get_user_favorites_count(user):
        """عدد عناصر المفضلة"""
        return Favorite.objects.filter(user=user).count()
    
    @staticmethod
    def toggle_favorite(user, course):
        """إضافة أو إزالة من المفضلة مع رسالة مناسبة"""
        favorite, created = Favorite.objects.get_or_create(user=user, course=course)
        if not created:
            favorite.delete()
            return False, 'تمت الإزالة من المفضلة'
        return True, 'تمت الإضافة إلى المفضلة'
    
    @staticmethod
    def is_favorite(user, course):
        """التحقق مما إذا كانت الدورة في المفضلة"""
        if not user.is_authenticated:
            return False
        return Favorite.objects.filter(user=user, course=course).exists()
    
    @staticmethod
    def get_most_favorited_courses(limit=5):
        """الدورات الأكثر إضافة للمفضلة"""
        return Course.objects.filter(
            is_active=True
        ).annotate(
            favorites_count=Count('favorited_by')
        ).order_by('-favorites_count')[:limit]

    @staticmethod
    def get_favorites_with_details(user):
        """المفضلة مع تفاصيل إضافية"""
        return Favorite.objects.filter(
            user=user
        ).select_related(
            'course', 'course__category', 'course__instructor'
        ).order_by('-created_at')



class ReviewService:
    """خدمات التقييمات"""
    
    @staticmethod
    def get_course_reviews(course):
        """الحصول على تقييمات الدورة"""
        return Review.objects.filter(course=course).select_related(
            'user'
        ).order_by('-created_at')
    
    @staticmethod
    def get_user_review(user, course):
        """الحصول على تقييم المستخدم لدورة معينة"""
        try:
            return Review.objects.get(user=user, course=course)
        except Review.DoesNotExist:
            return None
    
    @staticmethod
    def create_review(user, course, rating, comment):
        """إنشاء أو تحديث تقييم"""
        review, created = Review.objects.update_or_create(
            user=user,
            course=course,
            defaults={'rating': rating, 'comment': comment}
        )
        return review, created
    
    @staticmethod
    def delete_review(review_id, user):
        """حذف تقييم"""
        try:
            review = Review.objects.get(id=review_id, user=user)
            review.delete()
            return True
        except Review.DoesNotExist:
            return False
    
    @staticmethod
    def get_course_rating_stats(course_id):
        """إحصائيات التقييمات لدورة معينة"""
        reviews = Review.objects.filter(course_id=course_id)
        
        stats = {
            'total_reviews': reviews.count(),
            'average_rating': reviews.aggregate(avg=Avg('rating'))['avg'] or 0,
            'rating_distribution': {
                '5': reviews.filter(rating=5).count(),
                '4': reviews.filter(rating=4).count(),
                '3': reviews.filter(rating=3).count(),
                '2': reviews.filter(rating=2).count(),
                '1': reviews.filter(rating=1).count(),
            }
        }
        
        # حساب النسب المئوية
        if stats['total_reviews'] > 0:
            for rating in range(1, 6):
                stats['rating_distribution'][f'{rating}_percentage'] = (
                    stats['rating_distribution'][str(rating)] / stats['total_reviews'] * 100
                )
        
        return stats
    
    @staticmethod
    def get_recent_reviews(limit=5):
        """أحدث التقييمات"""
        return Review.objects.select_related(
            'user', 'course'
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_top_reviewed_courses(limit=5):
        """الدورات الأكثر تقييماً"""
        return Course.objects.filter(
            is_active=True,
            reviews__isnull=False
        ).annotate(
            reviews_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).order_by('-reviews_count', '-avg_rating')[:limit]

    @staticmethod
    def get_user_reviews_with_details(user):
        """تقييمات المستخدم مع تفاصيل إضافية"""
        return Review.objects.filter(
            user=user
        ).select_related(
            'course', 'course__category'
        ).order_by('-created_at')
    
    @staticmethod
    def can_review(user, course):
        """التحقق مما إذا كان المستخدم يمكنه تقييم الدورة"""
        from .models import Enrollment
        return Enrollment.objects.filter(
            user=user,
            course=course,
            status='enrolled'
        ).exists() or user.is_admin_user()


class UserService:
    """خدمات المستخدمين"""
    
    @staticmethod
    def get_user_stats(user_id):
        """إحصائيات المستخدم"""
        stats = {
            'enrolled_courses': Enrollment.objects.filter(user_id=user_id, status='enrolled').count(),
            'completed_courses': Enrollment.objects.filter(user_id=user_id, status='completed').count(),
            'favorite_courses': Favorite.objects.filter(user_id=user_id).count(),
            'reviews_written': Review.objects.filter(user_id=user_id).count(),
            'total_learning_hours': 0,
        }
        
        # حساب إجمالي ساعات التعلم
        enrollments = Enrollment.objects.filter(user_id=user_id, status='enrolled')
        for enrollment in enrollments:
            completed_lessons = LessonProgress.objects.filter(
                enrollment=enrollment,
                is_completed=True
            ).count()
            if completed_lessons > 0:
                lesson_duration = Lesson.objects.filter(
                    module__course=enrollment.course
                ).aggregate(total=Sum('duration_minutes'))['total'] or 0
                stats['total_learning_hours'] += (lesson_duration / 60) * (completed_lessons / Lesson.objects.filter(module__course=enrollment.course).count())
        
        return stats
    
    @staticmethod
    def get_learning_progress(user_id):
        """تقدم التعلم للمستخدم"""
        enrollments = Enrollment.objects.filter(user_id=user_id, status='enrolled')
        progress_data = []
        
        for enrollment in enrollments:
            total_lessons = Lesson.objects.filter(module__course=enrollment.course).count()
            completed_lessons = LessonProgress.objects.filter(
                enrollment=enrollment,
                is_completed=True
            ).count()
            
            progress_data.append({
                'course': enrollment.course,
                'progress': int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0,
                'completed_lessons': completed_lessons,
                'total_lessons': total_lessons,
                'last_accessed': enrollment.last_accessed,
            })
        
        return progress_data

class ModuleService:
    """خدمات الوحدات"""
    
    @staticmethod
    def get_module_with_lessons(module_id):
        """الحصول على الوحدة مع دروسها"""
        return CourseModule.objects.prefetch_related(
            'lessons'
        ).get(id=module_id)
    
    @staticmethod
    def get_course_modules(course_id):
        """الحصول على وحدات الدورة"""
        return CourseModule.objects.filter(course_id=course_id).prefetch_related(
            'lessons'
        ).order_by('order')
    
    @staticmethod
    def get_module_progress(module, user):
        """تقدم المستخدم في الوحدة"""
        if not user.is_authenticated:
            return 0
        
        try:
            enrollment = Enrollment.objects.get(
                user=user,
                course=module.course,
                status='enrolled'
            )
            
            total_lessons = module.lessons.count()
            completed_lessons = LessonProgress.objects.filter(
                enrollment=enrollment,
                lesson__in=module.lessons.all(),
                is_completed=True
            ).count()
            
            return int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
        except Enrollment.DoesNotExist:
            return 0

class LessonService:
    """خدمات الدروس"""
    
    @staticmethod
    def get_lesson_detail(lesson_id, user=None):
        """الحصول على تفاصيل الدرس"""
        lesson = Lesson.objects.select_related(
            'module', 'module__course'
        ).get(id=lesson_id)
        
        if user and user.is_authenticated:
            try:
                enrollment = Enrollment.objects.get(
                    user=user,
                    course=lesson.module.course,
                    status='enrolled'
                )
                progress = LessonProgress.objects.filter(
                    enrollment=enrollment,
                    lesson=lesson
                ).first()
                
                if progress:
                    lesson.user_progress = progress
                    lesson.is_completed = progress.is_completed
                    lesson.last_position = progress.last_watched_position
            except Enrollment.DoesNotExist:
                pass
        
        return lesson
    
    @staticmethod
    def mark_lesson_completed(user, lesson_id):
        """تحديد الدرس كمكتمل"""
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            enrollment = Enrollment.objects.get(
                user=user,
                course=lesson.module.course,
                status='enrolled'
            )
            
            progress, created = LessonProgress.objects.get_or_create(
                enrollment=enrollment,
                lesson=lesson
            )
            
            if not progress.is_completed:
                progress.is_completed = True
                progress.completed_at = timezone.now()
                progress.save()
                
                # تحديث تقدم الدورة
                enrollment.update_progress()
                
                return True
        except (Lesson.DoesNotExist, Enrollment.DoesNotExist):
            pass
        
        return False
    
    @staticmethod
    def update_lesson_position(user, lesson_id, position):
        """تحديث آخر موضع مشاهدة"""
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            enrollment = Enrollment.objects.get(
                user=user,
                course=lesson.module.course,
                status='enrolled'
            )
            
            progress, created = LessonProgress.objects.get_or_create(
                enrollment=enrollment,
                lesson=lesson
            )
            
            progress.last_watched_position = position
            progress.save()
            
            return True
        except (Lesson.DoesNotExist, Enrollment.DoesNotExist):
            return False
    
    @staticmethod
    def get_next_lesson(current_lesson):
        """الحصول على الدرس التالي"""
        return Lesson.objects.filter(
            module__course=current_lesson.module.course,
            order__gt=current_lesson.order
        ).order_by('order').first()
    
    @staticmethod
    def get_previous_lesson(current_lesson):
        """الحصول على الدرس السابق"""
        return Lesson.objects.filter(
            module__course=current_lesson.module.course,
            order__lt=current_lesson.order
        ).order_by('-order').first()

class DashboardService:
    """خدمات لوحة التحكم"""
    
    @staticmethod
    def get_admin_dashboard_stats():
        """إحصائيات لوحة تحكم الأدمن"""
        return {
            'total_users': User.objects.count(),
            'total_students': User.objects.filter(role='user').count(),
            'total_instructors': User.objects.filter(role='instructor').count(),
            'total_admins': User.objects.filter(role='admin').count(),
            'total_courses': Course.objects.count(),
            'active_courses': Course.objects.filter(is_active=True).count(),
            'total_enrollments': Enrollment.objects.count(),
            'pending_enrollments': Enrollment.objects.filter(status='pending').count(),
            'total_reviews': Review.objects.count(),
            'total_revenue': Enrollment.objects.filter(
                status='enrolled'
            ).aggregate(total=Sum('course__price'))['total'] or 0,
            'recent_users': User.objects.order_by('-date_joined')[:5],
            'recent_courses': Course.objects.order_by('-created_at')[:5],
            'recent_enrollments': Enrollment.objects.select_related(
                'user', 'course'
            ).order_by('-enrolled_at')[:5],
        }
    
    @staticmethod
    def get_instructor_dashboard_stats(instructor_id):
        """إحصائيات لوحة تحكم المدرب"""
        courses = Course.objects.filter(instructor_id=instructor_id)
        course_ids = courses.values_list('id', flat=True)
        
        return {
            'total_courses': courses.count(),
            'total_students': Enrollment.objects.filter(
                course__in=course_ids,
                status='enrolled'
            ).values('user').distinct().count(),
            'total_enrollments': Enrollment.objects.filter(
                course__in=course_ids
            ).count(),
            'pending_enrollments': Enrollment.objects.filter(
                course__in=course_ids,
                status='pending'
            ).count(),
            'total_revenue': Enrollment.objects.filter(
                course__in=course_ids,
                status='enrolled'
            ).aggregate(total=Sum('course__price'))['total'] or 0,
            'average_rating': courses.aggregate(avg=Avg('rating'))['avg'] or 0,
            'recent_enrollments': Enrollment.objects.filter(
                course__in=course_ids
            ).select_related('user', 'course').order_by('-enrolled_at')[:5],
        }
    
    @staticmethod
    def get_user_dashboard_stats(user_id):
        """إحصائيات لوحة تحكم المستخدم"""
        return {
            'enrolled_courses': Enrollment.objects.filter(
                user_id=user_id, 
                status='enrolled'
            ).count(),
            'completed_courses': Enrollment.objects.filter(
                user_id=user_id, 
                status='completed'
            ).count(),
            'favorite_courses': Favorite.objects.filter(
                user_id=user_id
            ).count(),
            'reviews_written': Review.objects.filter(
                user_id=user_id
            ).count(),
            'recent_enrollments': Enrollment.objects.filter(
                user_id=user_id
            ).select_related('course').order_by('-enrolled_at')[:3],
        }

class SearchService:
    """خدمات البحث المتقدم"""
    
    @staticmethod
    def global_search(query):
        """بحث شامل في جميع المحتويات"""
        results = {
            'courses': [],
            'instructors': [],
            'categories': [],
        }
        
        if query:
            # بحث في الدورات
            results['courses'] = Course.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(short_description__icontains=query),
                is_active=True
            )[:5]
            
            # بحث في المدربين
            results['instructors'] = User.objects.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(bio__icontains=query),
                role='instructor'
            )[:3]
            
            # بحث في التصنيفات
            results['categories'] = Category.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )[:3]
        
        return results
    
    @staticmethod
    def advanced_search(params):
        """بحث متقدم مع فلترة"""
        queryset = Course.objects.filter(is_active=True)
        
        if params.get('q'):
            queryset = queryset.filter(
                Q(title__icontains=params['q']) |
                Q(description__icontains=params['q'])
            )
        
        if params.get('category'):
            queryset = queryset.filter(category_id=params['category'])
        
        if params.get('level'):
            queryset = queryset.filter(level=params['level'])
        
        if params.get('min_price'):
            queryset = queryset.filter(price__gte=params['min_price'])
        
        if params.get('max_price'):
            queryset = queryset.filter(price__lte=params['max_price'])
        
        if params.get('min_rating'):
            queryset = queryset.filter(rating__gte=params['min_rating'])
        
        if params.get('instructor'):
            queryset = queryset.filter(instructor_id=params['instructor'])
        
        if params.get('has_certificate'):
            queryset = queryset.filter(has_certificate=True)
        
        if params.get('is_free'):
            queryset = queryset.filter(price=0)
        
        # الترتيب
        sort_by = params.get('sort', '-created_at')
        if sort_by in ['title', '-title', 'price', '-price', 'rating', '-rating', 'created_at', '-created_at']:
            queryset = queryset.order_by(sort_by)
        
        return queryset