from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone

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
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fa-folder')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
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
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_taught')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    duration_hours = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    students_count = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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
    
    class Meta:
        unique_together = ['user', 'course']
        indexes = [
            models.Index(fields=['status', 'user']),
            models.Index(fields=['course', 'status']),
        ]
    
    def update_progress(self):
        total_lessons = Lesson.objects.filter(module__course=self.course).count()
        if total_lessons > 0:
            completed_lessons = self.lesson_progress.filter(is_completed=True).count()
            self.progress = int((completed_lessons / total_lessons) * 100)
            
            if self.progress == 100 and self.status != 'completed':
                self.status = 'completed'
                self.completed_at = timezone.now()
            
            self.save(update_fields=['progress', 'status', 'completed_at'])
    
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