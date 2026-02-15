from django.contrib import admin
from django.utils.html import format_html
from .models import (
    User, Category, Course, CourseModule, 
    Lesson, Enrollment, Review, Favorite, LessonProgress
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'get_full_name', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_editable = ['role']
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('username', 'email', 'first_name', 'last_name', 'role', 'phone_number')
        }),
        ('معلومات إضافية', {
            'fields': ('bio', 'avatar')
        }),
        ('صلاحيات', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('تواريخ مهمة', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name() or '-'
    get_full_name.short_description = 'الاسم الكامل'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'get_courses_count', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['created_at']
    
    def get_courses_count(self, obj):
        return obj.courses.count()
    get_courses_count.short_description = 'عدد الدورات'

class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 1
    fields = ['title', 'order', 'description']

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'order', 'duration_minutes', 'is_free']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'instructor', 'price', 'level', 'rating', 'students_count', 'is_featured', 'is_active']
    list_filter = ['level', 'is_featured', 'is_active', 'category']
    search_fields = ['title', 'description', 'instructor__username']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['price', 'is_featured', 'is_active']
    readonly_fields = ['rating', 'students_count']
    inlines = [CourseModuleInline]
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('title', 'slug', 'category', 'instructor', 'image')
        }),
        ('وصف الدورة', {
            'fields': ('short_description', 'description')
        }),
        ('تفاصيل الدورة', {
            'fields': ('price', 'level', 'duration_hours', 'has_certificate')
        }),
        ('إحصائيات', {
            'fields': ('rating', 'students_count')
        }),
        ('حالة الدورة', {
            'fields': ('is_featured', 'is_active')
        }),
        ('تواريخ', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # إذا كان إنشاء جديد
            obj.instructor = request.user
        super().save_model(request, obj, form, change)

@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'get_lessons_count']
    list_filter = ['course']
    search_fields = ['title', 'course__title']
    inlines = [LessonInline]
    
    def get_lessons_count(self, obj):
        return obj.lessons.count()
    get_lessons_count.short_description = 'عدد الدروس'

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'order', 'duration_minutes', 'is_free', 'video_preview']
    list_filter = ['is_free', 'module__course']
    search_fields = ['title', 'content']
    list_editable = ['order', 'duration_minutes', 'is_free']
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('module', 'title', 'order')
        }),
        ('محتوى الدرس', {
            'fields': ('content', 'video_url', 'video_file')
        }),
        ('تفاصيل', {
            'fields': ('duration_minutes', 'is_free')
        }),
    )
    
    def video_preview(self, obj):
        if obj.video_url:
            return format_html('<a href="{}" target="_blank">مشاهدة</a>', obj.video_url)
        elif obj.video_file:
            return format_html('<a href="{}" target="_blank">مشاهدة</a>', obj.video_file.url)
        return '-'
    video_preview.short_description = 'معاينة الفيديو'

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'status', 'progress', 'enrolled_at', 'completed_at']
    list_filter = ['status', 'enrolled_at']
    search_fields = ['user__username', 'course__title', 'notes']
    list_editable = ['status', 'progress']
    readonly_fields = ['enrolled_at', 'completed_at']
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('user', 'course', 'status')
        }),
        ('تقدم', {
            'fields': ('progress', 'notes')
        }),
        ('تواريخ', {
            'fields': ('enrolled_at', 'completed_at', 'last_accessed')
        }),
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'rating', 'short_comment', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'course__title', 'comment']
    list_editable = ['rating']
    
    def short_comment(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    short_comment.short_description = 'التعليق'

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'course__title']

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'lesson', 'is_completed', 'completed_at']
    list_filter = ['is_completed', 'completed_at']
    search_fields = ['enrollment__user__username', 'lesson__title']