from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class Notification(models.Model):
    """
    نموذج الإشعارات للمستخدمين
    """
    NOTIFICATION_TYPES = (
        ('info', 'معلومات'),
        ('success', 'نجاح'),
        ('warning', 'تحذير'),
        ('error', 'خطأ'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    # محتوى الإشعار
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    
    # رابط الإشعار (اختياري)
    link = models.CharField(max_length=500, blank=True, null=True)
    
    # صورة أو أيقونة (اختياري)
    icon = models.CharField(max_length=50, blank=True, null=True, 
                           help_text="اسم أيقونة Font Awesome (مثال: fa-user)")
    
    # حالة الإشعار
    is_read = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    
    # تواريخ
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'notification_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        """تحديد الإشعار كمقروء"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    @classmethod
    def create_notification(cls, user, title, message, notification_type='info', link=None, icon=None):
        """إنشاء إشعار جديد"""
        notification = cls(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link,
            icon=icon
        )
        notification.save()
        return notification
    
    @classmethod
    def get_unread_count(cls, user):
        """الحصول على عدد الإشعارات غير المقروءة"""
        return cls.objects.filter(user=user, is_read=False).count()
    
    @classmethod
    def mark_all_as_read(cls, user):
        """تحديد كل إشعارات المستخدم كمقروءة"""
        cls.objects.filter(user=user, is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )