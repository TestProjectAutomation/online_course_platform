from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    USER_ROLES = (
        ('admin', 'Admin'),
        ('user', 'User'),
        ('instructor', 'Instructor'),
    )
    
    role = models.CharField(max_length=10, choices=USER_ROLES, default='user')
    phone_number = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_joined']
    
    def is_admin_user(self):
        return self.role == 'admin' or self.is_superuser
    
    def is_instructor(self):
        return self.role == 'instructor'
    
    def get_enrolled_courses(self):
        return self.enrollments.filter(status='enrolled').select_related('course')
    
    def get_completed_courses(self):
        return self.enrollments.filter(status='completed').select_related('course')
    
    def get_purchased_courses(self):
        """الحصول على جميع الدورات المشتراة (مدى الحياة)"""
        return Course.objects.filter(
            enrollments__user=self,
            enrollments__status='enrolled',
            enrollments__has_lifetime_access=True
        )
    
    def has_course_access(self, course):
        """التحقق من وصول المستخدم لدورة معينة"""
        try:
            enrollment = Enrollment.objects.get(user=self, course=course)
            return enrollment.has_access
        except Enrollment.DoesNotExist:
            return False

    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fa-folder', blank=True, null=True)
    img_gat = models.ImageField(  # تأكد من أن اسم الحقل img_gat
        verbose_name="صورة التصنيف",
        upload_to='categories/',  # سيتم رفع الصور إلى media/categories/
        null=True, 
        blank=True
    )
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
            
            
    def get_courses_count(self):
        return self.courses.filter(is_active=True).count()
    
    def __str__(self):
        return self.name

class Course(models.Model):
    LEVEL_CHOICES = (
        ('beginner', 'مبتدئ'),
        ('intermediate', 'متوسط'),
        ('advanced', 'متقدم'),
        ('all', 'جميع المستويات'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='courses/')
    vidost_url = models.URLField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_taught')
    price = models.DecimalField(max_digits=10, decimal_places=2)
     # حقول الخصم
    discount_percent = models.IntegerField(
        _("نسبة الخصم"), 
        default=0,
        help_text="نسبة الخصم (0-100%)",
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    discount_start_date = models.DateTimeField(
        _("تاريخ بداية الخصم"), 
        null=True, 
        blank=True
    )
    discount_end_date = models.DateTimeField(
        _("تاريخ نهاية الخصم"), 
        null=True, 
        blank=True
    )
    is_discounted = models.BooleanField(_("مخفض"), default=False)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    duration_hours = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    students_count = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    views_count = models.IntegerField(default=0)  # أضف هذا السطر
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    video_url = models.URLField(
        _("رابط يوتيوب"), 
        blank=True, 
        null=True,
        help_text="رابط فيديو يوتيوب (مثال: https://www.youtube.com/watch?v=...)"
    )
    video_file = models.FileField(
        _("ملف فيديو"), 
        upload_to='courses/videos/',
        blank=True, 
        null=True,
        help_text="رفع ملف فيديو (mp4, webm, etc)"
    )
    
    
    
    @property
    def has_discount(self):
        """التحقق من وجود خصم ساري"""
        now = timezone.now()
        return (self.discount_percent > 0 and 
                self.discount_start_date and 
                self.discount_end_date and 
                self.discount_start_date <= now <= self.discount_end_date)
    
    @property
    def discounted_price(self):
        """حساب السعر بعد الخصم"""
        if self.has_discount:
            return self.price * (100 - self.discount_percent) / 100
        return self.price
    
    @property
    def discount_status(self):
        """حالة الخصم"""
        if not self.has_discount:
            return None
        now = timezone.now()
        if self.discount_end_date:
            days_left = (self.discount_end_date - now).days
            if days_left <= 1:
                return 'ending_soon'
            elif days_left <= 3:
                return 'last_chance'
            else:
                return 'active'
        return 'active'
    
    @property
    def discount_ends_in(self):
        """الوقت المتبقي للخصم"""
        if self.has_discount and self.discount_end_date:
            delta = self.discount_end_date - timezone.now()
            days = delta.days
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            
            if days > 0:
                return f"{days} يوم"
            elif hours > 0:
                return f"{hours} ساعة"
            elif minutes > 0:
                return f"{minutes} دقيقة"
            else:
                return "ينتهي قريباً"
        return None


    @property
    def has_video_preview(self):
        """التحقق من وجود فيديو تعريفي"""
        return bool(self.video_url or self.video_file)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['category', 'level']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('course_detail', args=[self.slug])
    
    def update_rating(self):
        reviews = self.reviews.all()
        if reviews:
            self.rating = sum(r.rating for r in reviews) / len(reviews)
            self.save(update_fields=['rating'])
    
    def get_modules_count(self):
        return self.modules.count()
    
    def get_lessons_count(self):
        return Lesson.objects.filter(module__course=self).count()
    
    def get_total_duration(self):
        total = Lesson.objects.filter(module__course=self).aggregate(
            total=models.Sum('duration_minutes')
        )['total'] or 0
        return total
    
    def get_enrolled_students(self):
        return self.enrollments.filter(status='enrolled').count()
    
    def is_enrolled(self, user):
        if user.is_authenticated:
            return self.enrollments.filter(user=user, status='enrolled').exists()
        return False
    
    def __str__(self):
        return self.title

class CourseModule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def get_lessons_count(self):
        return self.lessons.count()
    
    def get_total_duration(self):
        return self.lessons.aggregate(
            total=models.Sum('duration_minutes')
        )['total'] or 0
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    video_url = models.URLField(blank=True)
    video_file = models.FileField(upload_to='lessons/', null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)
    content = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_free = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['module', 'order']),
        ]
    
    def get_video_url(self):
        if self.video_file:
            return self.video_file.url
        return self.video_url
    
    def is_watched_by_user(self, user):
        if user.is_authenticated:
            enrollment = Enrollment.objects.filter(
                user=user, 
                course=self.module.course,
                status='enrolled'
            ).first()
            if enrollment:
                return LessonProgress.objects.filter(
                    enrollment=enrollment,
                    lesson=self,
                    is_completed=True
                ).exists()
        return False
    
    def __str__(self):
        return self.title

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'قيد الانتظار'),
        ('enrolled', 'مسجل'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    
    has_lifetime_access = models.BooleanField(_("وصول مدى الحياة"), default=True)
    access_expires_at = models.DateTimeField(_("تاريخ انتهاء الوصول"), null=True, blank=True)


    class Meta:
        unique_together = ['user', 'course']
        indexes = [
            models.Index(fields=['status', 'user']),
            models.Index(fields=['course', 'status']),
            models.Index(fields=['user', 'has_lifetime_access']),
        ]
    
    def update_progress(self):
        total_lessons = Lesson.objects.filter(module__course=self.course).count()
        if total_lessons > 0:
            completed_lessons = self.lesson_progress.filter(is_completed=True).count()
            self.progress = int((completed_lessons / total_lessons) * 100)
            
            if self.progress == 100 and self.status != 'completed':
                self.status = 'completed'
                self.completed_at = timezone.now()
                
                # ✅ إنشاء إشعار بإكمال الدورة
                from .utils import notify_course_completed
                notify_course_completed(self)
            
            self.save(update_fields=['progress', 'status', 'completed_at'])
    def notify_course_completed(enrollment):
        """إرسال إشعار عند إكمال الدورة"""
        from .models import Notification
        
        Notification.objects.create(
            user=enrollment.user,
            title="🎉 تهانينا! لقد أكملت الدورة",
            message=f"لقد أكملت بنجاح دورة {enrollment.course.title}. لا يزال لديك وصول مدى الحياة لمحتوى الدورة",
            notification_type='success',
            link=f"/course/{enrollment.course.slug}/",
            icon="fa-graduation-cap"
        )

    @property
    def has_access(self):
        """التحقق مما إذا كان المستخدم لا يزال لديه حق الوصول"""
        if self.has_lifetime_access:
            return True
        if self.access_expires_at:
            return timezone.now() <= self.access_expires_at
        return self.status == 'enrolled'
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.get_status_display()})"


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_watched_position = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['enrollment', 'lesson']
    
    def save(self, *args, **kwargs):
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)
        self.enrollment.update_progress()
    
    def __str__(self):
        return f"{self.enrollment.user.username} - {self.lesson.title}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.course.update_rating()
    
    def delete(self, *args, **kwargs):
        course = self.course
        super().delete(*args, **kwargs)
        course.update_rating()
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.rating}/5)"
    
    
    
class Order(models.Model):
    """نموذج الطلبات"""
    STATUS_CHOICES = (
        ('pending', 'قيد الانتظار'),
        ('processing', 'قيد المعالجة'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)
    
    # معلومات التواصل
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'طلب'
        verbose_name_plural = 'الطلبات'
    
    def __str__(self):
        return f"طلب #{self.id} - {self.user.username} - {self.total} ج.م"
    
    def get_items_count(self):
        return self.items.count()

class OrderItem(models.Model):
    """عناصر الطلب"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'عنصر الطلب'
        verbose_name_plural = 'عناصر الطلبات'
    
    def __str__(self):
        return f"{self.order.id} - {self.course.title}"
    
