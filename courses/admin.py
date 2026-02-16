from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.db import models
from django.utils import timezone
from rangefilter.filters import DateRangeFilter
from import_export.admin import ImportExportModelAdmin
from .models import (
    User, Category, Course, CourseModule, Lesson,
    Favorite, Enrollment, LessonProgress, Review
)

# =========================
# ADMIN ACTIONS
# =========================
@admin.action(description='Activate selected items')
def activate_items(modeladmin, request, queryset):
    queryset.update(is_active=True)

@admin.action(description='Deactivate selected items')
def deactivate_items(modeladmin, request, queryset):
    queryset.update(is_active=False)

@admin.action(description='Update ratings for selected courses')
def update_courses_rating(modeladmin, request, queryset):
    for course in queryset:
        course.update_rating()
    modeladmin.message_user(request, 'Ratings updated successfully')

# =========================
# INLINE MODELS
# =========================
class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 1
    fields = ['title', 'order', 'get_lessons_count']
    readonly_fields = ['get_lessons_count']
    show_change_link = True
    
    def get_lessons_count(self, obj):
        if obj.pk:
            count = obj.lessons.count()
            url = reverse('admin:courses_lesson_changelist') + f'?module__id__exact={obj.pk}'
            return format_html('<a href="{}">{} lessons</a>', url, count)
        return '0'
    get_lessons_count.short_description = 'Lessons'

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'order', 'duration_minutes', 'is_free']
    
class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    fields = ['user', 'status', 'progress', 'enrolled_at']
    readonly_fields = ['enrolled_at']
    show_change_link = True
    
class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ['user', 'rating', 'comment_short']
    readonly_fields = ['comment_short']
    
    def comment_short(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_short.short_description = 'Comment'

# =========================
# USER ADMIN
# =========================
@admin.register(User)
class UserAdmin(BaseUserAdmin, ImportExportModelAdmin):
    list_display = [
        'username', 'email', 'get_full_name', 'role', 
        'get_enrollments_count', 'is_active', 'date_joined_display'
    ]
    list_filter = [
        'role', 'is_active', 'is_staff', 'is_superuser',
        'date_joined',
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_editable = ['role']
    list_per_page = 25
    date_hierarchy = 'date_joined'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('username', 'email', 'password'),
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone_number', 'bio', 'avatar'),
            'classes': ('collapse',),
        }),
        ('Permissions & Role', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',),
        }),
    )
    
    inlines = [EnrollmentInline, ReviewInline]
    
    def get_enrollments_count(self, obj):
        count = obj.enrollments.filter(status='enrolled').count()
        return count
    get_enrollments_count.short_description = 'Enrollments'
    
    def date_joined_display(self, obj):
        return obj.date_joined.strftime('%Y-%m-%d')
    date_joined_display.short_description = 'Joined'
    date_joined_display.admin_order_field = 'date_joined'
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            enrollments_count=models.Count('enrollments', filter=models.Q(enrollments__status='enrolled'))
        )
    
    actions = [activate_items, deactivate_items]


# =========================
# CATEGORY ADMIN
# =========================
@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    list_display = [
        'name', 'slug', 'parent', 'get_courses_count', 
        'created_at_date', 'has_image'  # أضفنا عمود للصورة
    ]
    list_filter = ['parent', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 25
    
    fieldsets = (
        ('Category Info', {
            'fields': ('name', 'slug', 'parent', 'icon')
        }),
        ('Category Image', {  # قسم جديد للصورة
            'fields': ('img_gat',),
            'classes': ('wide',),
            'description': 'رفع صورة تمثل التصنيف (يفضل 300x300 بكسل)'
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('wide',),
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    
    def get_courses_count(self, obj):
        return obj.courses.filter(is_active=True).count()
    get_courses_count.short_description = 'Courses'
    
    def created_at_date(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_date.short_description = 'Created'
    created_at_date.admin_order_field = 'created_at'
    
    # إضافة دالة للتحقق من وجود صورة
    def has_image(self, obj):
        if obj.img_gat:
            return True
        return False
    has_image.boolean = True  # يعرض أيقونة صح/خطأ
    has_image.short_description = 'Image'
    
    # إضافة معاينة للصورة في صفحة التعديل
    def image_preview(self, obj):
        if obj.img_gat:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px; border-radius: 8px; border: 2px solid #3b82f6;" />',
                obj.img_gat.url
            )
        return "لا توجد صورة"
    image_preview.short_description = 'معاينة الصورة'


# =========================
# COURSE ADMIN
# =========================
@admin.register(Course)
class CourseAdmin(ImportExportModelAdmin):
    list_display = [
        'title', 'instructor', 'category', 'price_display', 
        'level', 'rating_display', 'get_students_count', 
        'is_active', 'is_featured', 'created_at_date'
    ]
    list_filter = [
        'level', 'is_active', 'is_featured', 'category',
        'instructor', 'created_at',
    ]
    search_fields = ['title']
    list_editable = ['is_active', 'is_featured', 'level']
    list_per_page = 25
    date_hierarchy = 'created_at'
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'instructor')
        }),
        ('Description', {
            'fields': ('short_description', 'description', 'image', 'vidost_url'),
            'classes': ('wide',),
        }),
        ('Course Details', {
            'fields': ('price', 'level', 'duration_hours', 'views_count'),
        }),
        ('Statistics', {
            'fields': ('students_count', 'rating', 'is_featured', 'is_active'),
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['students_count', 'rating', 'created_at', 'updated_at']
    inlines = [CourseModuleInline]
    
    actions = [activate_items, deactivate_items, update_courses_rating]
    
    def price_display(self, obj):
        return format_html('{} $', obj.price)
    price_display.short_description = 'Price'
    price_display.admin_order_field = 'price'
    
    def rating_display(self, obj):
        stars = '★' * int(obj.rating) + '☆' * (5 - int(obj.rating))
        return format_html(
            '<span title="{}">{}</span>',
            obj.rating, stars
        )
    rating_display.short_description = 'Rating'
    
    def get_students_count(self, obj):
        return obj.get_enrolled_students()
    get_students_count.short_description = 'Students'
    
    def created_at_date(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_date.short_description = 'Created'
    created_at_date.admin_order_field = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'category', 'instructor'
        )

# =========================
# COURSE MODULE ADMIN
# =========================
@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'course', 'order', 
        'get_lessons_count'
    ]
    list_filter = ['course']
    search_fields = ['title']
    list_editable = ['order']
    list_per_page = 25
    
    fieldsets = (
        ('Module Info', {
            'fields': ('course', 'title', 'order')
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('wide',),
        }),
    )
    
    inlines = [LessonInline]
    
    def get_lessons_count(self, obj):
        return obj.lessons.count()
    get_lessons_count.short_description = 'Lessons'

# =========================
# LESSON ADMIN
# =========================
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'module', 'order', 'duration_minutes', 
        'is_free', 'get_course', 'video_type'
    ]
    list_filter = [
        'is_free', 'module__course',
    ]
    search_fields = ['title']
    list_editable = ['order', 'is_free']
    list_per_page = 25
    
    fieldsets = (
        ('Lesson Info', {
            'fields': ('module', 'title', 'order', 'is_free')
        }),
        ('Content', {
            'fields': ('content', 'video_url', 'video_file', 'duration_minutes'),
            'classes': ('wide',),
        }),
    )
    
    def get_course(self, obj):
        return obj.module.course
    get_course.short_description = 'Course'
    get_course.admin_order_field = 'module__course'
    
    def video_type(self, obj):
        if obj.video_file:
            return 'File'
        elif obj.video_url:
            return 'URL'
        return 'None'
    video_type.short_description = 'Type'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'module__course'
        )

# =========================
# ENROLLMENT ADMIN
# =========================
@admin.register(Enrollment)
class EnrollmentAdmin(ImportExportModelAdmin):
    list_display = [
        'user', 'course', 'status', 'progress', 
        'enrolled_at_date', 'completed_at_date'
    ]
    list_filter = [
        'status', 'enrolled_at', 'course'
    ]
    search_fields = ['user__username', 'course__title']
    list_editable = ['status']
    list_per_page = 25
    date_hierarchy = 'enrolled_at'
    
    fieldsets = (
        ('Enrollment Info', {
            'fields': ('user', 'course', 'status', 'notes')
        }),
        ('Progress', {
            'fields': ('progress', 'last_accessed'),
            'classes': ('wide',),
        }),
        ('Dates', {
            'fields': ('enrolled_at', 'completed_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['progress', 'enrolled_at', 'last_accessed']
    
    def enrolled_at_date(self, obj):
        return obj.enrolled_at.strftime('%Y-%m-%d')
    enrolled_at_date.short_description = 'Enrolled'
    enrolled_at_date.admin_order_field = 'enrolled_at'
    
    def completed_at_date(self, obj):
        if obj.completed_at:
            return obj.completed_at.strftime('%Y-%m-%d')
        return '—'
    completed_at_date.short_description = 'Completed'
    
    actions = ['mark_as_enrolled', 'mark_as_completed', 'mark_as_cancelled']
    
    @admin.action(description='Mark as enrolled')
    def mark_as_enrolled(modeladmin, request, queryset):
        queryset.update(status='enrolled')
    
    @admin.action(description='Mark as completed')
    def mark_as_completed(modeladmin, request, queryset):
        now = timezone.now()
        queryset.update(status='completed', completed_at=now, progress=100)
    
    @admin.action(description='Mark as cancelled')
    def mark_as_cancelled(modeladmin, request, queryset):
        queryset.update(status='cancelled')

# =========================
# LESSON PROGRESS ADMIN
# =========================
@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'lesson', 'course', 'is_completed', 
        'completed_at_date'
    ]
    list_filter = ['is_completed', 'completed_at']
    search_fields = ['enrollment__user__username']
    list_per_page = 25
    
    def user(self, obj):
        return obj.enrollment.user
    user.short_description = 'User'
    
    def course(self, obj):
        return obj.enrollment.course
    course.short_description = 'Course'
    
    def completed_at_date(self, obj):
        if obj.completed_at:
            return obj.completed_at.strftime('%Y-%m-%d')
        return '—'
    completed_at_date.short_description = 'Completed'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'enrollment__user', 'enrollment__course', 'lesson'
        )

# =========================
# REVIEW ADMIN
# =========================
@admin.register(Review)
class ReviewAdmin(ImportExportModelAdmin):
    list_display = [
        'user', 'course', 'rating', 'comment_short', 
        'created_at_date'
    ]
    list_filter = [
        'rating', 'created_at', 'course'
    ]
    search_fields = ['user__username', 'comment']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Review Info', {
            'fields': ('user', 'course', 'rating')
        }),
        ('Comment', {
            'fields': ('comment',),
            'classes': ('wide',),
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def comment_short(self, obj):
        if len(obj.comment) > 50:
            return obj.comment[:50] + '...'
        return obj.comment
    comment_short.short_description = 'Comment'
    
    def created_at_date(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_date.short_description = 'Created'
    created_at_date.admin_order_field = 'created_at'

# =========================
# FAVORITE ADMIN
# =========================
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'created_at_date']
    list_filter = ['created_at', 'course']
    search_fields = ['user__username']
    list_per_page = 25
    
    def created_at_date(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_date.short_description = 'Added'
    created_at_date.admin_order_field = 'created_at'