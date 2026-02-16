from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid

# =================== Core Models ===================

class SiteSettings(models.Model):
    """
    إعدادات الموقع العامة
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # ✅ إعدادات الموقع الأساسية
    site_name = models.CharField(
        _("اسم الموقع"), 
        max_length=255, 
        null=True, 
        blank=True,
        help_text=_("اسم الموقع")
    )
    
    site_title = models.CharField(
        _("عنوان الموقع"), 
        max_length=255, 
        null=True, 
        blank=True,
        help_text=_("العنوان الذي يظهر في شريط المتصفح")
    )
    
    site_description = models.TextField(
        _("وصف الموقع"), 
        null=True, 
        blank=True,
        help_text=_("وصف مختصر للموقع لمحركات البحث")
    )
    
    site_keywords = models.CharField(
        _("الكلمات المفتاحية"), 
        max_length=500, 
        null=True, 
        blank=True,
        help_text=_("كلمات مفتاحية مفصولة بفواصل لمحركات البحث")
    )
    
    # ✅ معلومات التواصل
    site_email = models.EmailField(
        _("البريد الإلكتروني"), 
        max_length=255, 
        null=True, 
        blank=True,
        help_text=_("بريد التواصل الرسمي للموقع")
    )
    site_phone = models.CharField(
        _("رقم الهاتف"), 
        max_length=255, 
        null=True, 
        blank=True,
        help_text=_("رقم التواصل الرسمي للموقع")
    )
    site_whatsapp = models.CharField(
        _("رقم واتساب"), 
        max_length=255, 
        null=True, 
        blank=True,
        help_text=_("رقم الواتساب للتواصل السريع")
    )
    
    # ✅ العنوان
    site_address = models.CharField(
        _("العنوان"), 
        max_length=255, 
        null=True, 
        blank=True,
        help_text=_("العنوان الكامل")
    )
    
    # ✅ روابط التواصل الاجتماعي
    facebook_url = models.URLField(
        _("رابط Facebook"), 
        max_length=255, 
        null=True, 
        blank=True,
        help_text=_("رابط صفحة الفيسبوك")
    )
    twitter_url = models.URLField(
        _("رابط Twitter"), 
        max_length=255, 
        null=True, 
        blank=True,
        help_text=_("رابط حساب تويتر")
    )
    instagram_url = models.URLField(
        _("رابط Instagram"), 
        max_length=255, 
        null=True, 
        blank=True,
        help_text=_("رابط حساب انستغرام")
    )
    linkedin_url = models.URLField(
        _("رابط LinkedIn"), 
        max_length=255, 
        null=True, 
        blank=True,
        help_text=_("رابط صفحة لينكد إن")
    )
    youtube_url = models.URLField(
        _("رابط YouTube"), 
        max_length=255, 
        null=True, 
        blank=True,
        help_text=_("رابط قناة اليوتيوب")
    )
    
    # ✅ الشعارات والصور
    site_logo = models.ImageField(
        _("شعار الموقع"), 
        upload_to='site/logo/', 
        null=True, 
        blank=True,
        help_text=_("الشعار الرئيسي للموقع (يُفضل PNG بخلفية شفافة)")
    )
    site_logo_white = models.ImageField(
        _("شعار الموقع (أبيض)"), 
        upload_to='site/logo/', 
        null=True, 
        blank=True,
        help_text=_("شعار أبيض للخلفيات الداكنة")
    )
    site_favicon = models.ImageField(
        _("أيقونة الموقع"), 
        upload_to='site/favicon/', 
        null=True, 
        blank=True,
        help_text=_("الأيقونة التي تظهر في شريط المتصفح (32x32 بكسل)")
    )
    site_icon = models.ImageField(
        _("أيقونة التطبيق"), 
        upload_to='site/icon/', 
        null=True, 
        blank=True,
        help_text=_("أيقونة التطبيق للهواتف (192x192 بكسل)")
    )
    site_og_image = models.ImageField(
        _("صورة المشاركة"), 
        upload_to='site/og/', 
        null=True, 
        blank=True,
        help_text=_("الصورة التي تظهر عند مشاركة الرابط (1200x630 بكسل)")
    )
    
    # ✅ إعدادات إضافية
    meta_author = models.CharField(
        _("المؤلف"), 
        max_length=255, 
        null=True, 
        blank=True,
        default="NextJobs Team",
        help_text=_("اسم المؤلف أو الشركة المطورة")
    )
    
    copyright_text = models.CharField(
        _("نص حقوق النشر"), 
        max_length=500, 
        null=True, 
        blank=True,
        default="جميع الحقوق محفوظة © NextJobs",
        help_text=_("نص حقوق النشر الذي يظهر في التذييل")
    )
    
    google_analytics_id = models.CharField(
        _("معرف Google Analytics"), 
        max_length=50, 
        null=True, 
        blank=True,
        help_text=_("مثال: G-XXXXXXXXXX")
    )
    google_site_verification = models.CharField(
        _("رمز التحقق Google"), 
        max_length=100, 
        null=True, 
        blank=True,
        help_text=_("رمز التحقق من ملكية الموقع في Google")
    )
    
    # ✅ إعدادات البريد الإلكتروني
    smtp_server = models.CharField(
        _("خادم SMTP"), 
        max_length=255, 
        null=True, 
        blank=True,
        default="smtp.gmail.com"
    )
    smtp_port = models.IntegerField(
        _("منفذ SMTP"), 
        null=True, 
        blank=True,
        default=587
    )
    smtp_username = models.CharField(
        _("اسم مستخدم SMTP"), 
        max_length=255, 
        null=True, 
        blank=True
    )
    smtp_password = models.CharField(
        _("كلمة مرور SMTP"), 
        max_length=255, 
        null=True, 
        blank=True
    )
    smtp_use_tls = models.BooleanField(
        _("استخدام TLS"), 
        default=True,
        help_text=_("تفعيل تشفير TLS للبريد الإلكتروني")
    )
    
    # ✅ إعدادات الموقع
    is_active = models.BooleanField(
        _("نشط"), 
        default=True,
        help_text=_("تفعيل هذا الإعداد كإعدادات الموقع الرئيسية")
    )
    maintenance_mode = models.BooleanField(
        _("وضع الصيانة"), 
        default=False,
        help_text=_("تفعيل وضع الصيانة - سيظهر الموقع تحت الصيانة")
    )
    
    # ✅ تواريخ الإنشاء والتحديث
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)
    
    class Meta:
        verbose_name = _("إعدادات الموقع")
        verbose_name_plural = _("إعدادات الموقع")
        ordering = ['-created_at']
    
    def __str__(self):
        return self.site_name or "إعدادات الموقع"
    
    def save(self, *args, **kwargs):
        """ضمان وجود إعدادات واحدة فقط نشطة"""
        if self.is_active:
            SiteSettings.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active_settings(cls):
        """الحصول على الإعدادات النشطة"""
        return cls.objects.filter(is_active=True).first()
    
    @classmethod
    def get_site_name(cls):
        """الحصول على اسم الموقع"""
        settings = cls.get_active_settings()
        return settings.site_name if settings else "NextJobs"
    
    @classmethod
    def get_site_logo(cls):
        """الحصول على شعار الموقع"""
        settings = cls.get_active_settings()
        return settings.site_logo if settings else None
    
    @classmethod
    def get_site_favicon(cls):
        """الحصول على أيقونة الموقع"""
        settings = cls.get_active_settings()
        return settings.site_favicon if settings else None


class ContactMessage(models.Model):
    """
    نموذج رسائل التواصل من الزوار
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(_("الاسم"), max_length=255)
    email = models.EmailField(_("البريد الإلكتروني"), max_length=255)
    phone = models.CharField(_("رقم الهاتف"), max_length=50, blank=True, null=True)
    
    subject = models.CharField(_("الموضوع"), max_length=255)
    message = models.TextField(_("الرسالة"))
    
    # ✅ حالة الرسالة
    is_read = models.BooleanField(_("تمت القراءة"), default=False)
    is_replied = models.BooleanField(_("تم الرد"), default=False)
    replied_at = models.DateTimeField(_("تاريخ الرد"), blank=True, null=True)
    replied_by = models.CharField(_("تم الرد بواسطة"), max_length=255, blank=True, null=True)
    reply_message = models.TextField(_("نص الرد"), blank=True, null=True)
    
    # ✅ معلومات إضافية
    ip_address = models.GenericIPAddressField(_("عنوان IP"), blank=True, null=True)
    user_agent = models.TextField(_("متصفح المستخدم"), blank=True, null=True)
    
    created_at = models.DateTimeField(_("تاريخ الإرسال"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)
    
    class Meta:
        verbose_name = _("رسالة تواصل")
        verbose_name_plural = _("رسائل التواصل")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_read']),
            models.Index(fields=['is_replied']),
            models.Index(fields=['created_at']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
    
    def mark_as_read(self):
        """تحديد الرسالة كمقروءة"""
        self.is_read = True
        self.save(update_fields=['is_read'])
    
    def mark_as_replied(self, replied_by=None, reply_message=None):
        """تحديد الرسالة كتم الرد عليها"""
        from django.utils import timezone
        self.is_replied = True
        self.replied_at = timezone.now()
        if replied_by:
            self.replied_by = replied_by
        if reply_message:
            self.reply_message = reply_message
        self.save(update_fields=['is_replied', 'replied_at', 'replied_by', 'reply_message'])


class NewsletterSubscriber(models.Model):
    """
    نموذج المشتركين في النشرة البريدية
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    email = models.EmailField(_("البريد الإلكتروني"), max_length=255, unique=True)
    name = models.CharField(_("الاسم"), max_length=255, blank=True, null=True)
    
    # ✅ حالة الاشتراك
    is_active = models.BooleanField(_("نشط"), default=True)
    is_verified = models.BooleanField(_("موثق"), default=False)
    verification_token = models.CharField(_("رمز التوثيق"), max_length=100, blank=True, null=True)
    verified_at = models.DateTimeField(_("تاريخ التوثيق"), blank=True, null=True)
    
    # ✅ إعدادات الاشتراك
    receive_job_alerts = models.BooleanField(_("استلام تنبيهات الوظائف"), default=True)
    receive_newsletter = models.BooleanField(_("استلام النشرة البريدية"), default=True)
    
    ip_address = models.GenericIPAddressField(_("عنوان IP"), blank=True, null=True)
    
    created_at = models.DateTimeField(_("تاريخ الاشتراك"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)
    unsubscribed_at = models.DateTimeField(_("تاريخ إلغاء الاشتراك"), blank=True, null=True)
    
    class Meta:
        verbose_name = _("مشترك في النشرة البريدية")
        verbose_name_plural = _("المشتركون في النشرة البريدية")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.email
    
    def verify(self):
        """توثيق البريد الإلكتروني"""
        from django.utils import timezone
        self.is_verified = True
        self.verified_at = timezone.now()
        self.verification_token = None
        self.save(update_fields=['is_verified', 'verified_at', 'verification_token'])
    
    def unsubscribe(self):
        """إلغاء الاشتراك"""
        from django.utils import timezone
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save(update_fields=['is_active', 'unsubscribed_at'])


class Testimonial(models.Model):
    """
    نموذج شهادات العملاء
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(_("الاسم"), max_length=255)
    position = models.CharField(_("المسمى الوظيفي"), max_length=255)
    company = models.CharField(_("الشركة"), max_length=255)
    content = models.TextField(_("نص الشهادة"))
    
    # ✅ الصور
    avatar = models.ImageField(
        _("الصورة الشخصية"), 
        upload_to='testimonials/avatars/', 
        null=True, 
        blank=True
    )
    company_logo = models.ImageField(
        _("شعار الشركة"), 
        upload_to='testimonials/logos/', 
        null=True, 
        blank=True
    )
    
    # ✅ التقييم
    rating = models.PositiveIntegerField(
        _("التقييم"), 
        choices=[(i, f"{i} {_('نجوم')}") for i in range(1, 6)],
        default=5
    )
    
    # ✅ حالة الشهادة
    is_active = models.BooleanField(_("نشط"), default=True)
    is_featured = models.BooleanField(_("مميز"), default=False)
    order = models.PositiveIntegerField(_("الترتيب"), default=0)
    
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)
    
    class Meta:
        verbose_name = _("شهادة عميل")
        verbose_name_plural = _("شهادات العملاء")
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['order']),
            models.Index(fields=['rating']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.company}"


class Partner(models.Model):
    """
    نموذج شركاء الموقع
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(_("اسم الشريك"), max_length=255)
    description = models.TextField(_("وصف الشريك"), blank=True, null=True)
    
    # ✅ الصور
    logo = models.ImageField(
        _("شعار الشريك"), 
        upload_to='partners/logos/', 
        null=True, 
        blank=True
    )
    website_url = models.URLField(_("رابط الموقع"), max_length=255, blank=True, null=True)
    
    # ✅ حالة الشريك
    is_active = models.BooleanField(_("نشط"), default=True)
    is_featured = models.BooleanField(_("مميز"), default=False)
    order = models.PositiveIntegerField(_("الترتيب"), default=0)
    
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)
    
    class Meta:
        verbose_name = _("شريك")
        verbose_name_plural = _("الشركاء")
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['order']),
        ]
    
    def __str__(self):
        return self.name


class FAQ(models.Model):
    """
    نموذج الأسئلة الشائعة
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    question = models.CharField(_("السؤال"), max_length=500)
    answer = models.TextField(_("الإجابة"))
    
    # ✅ تصنيف السؤال
    category_choices = [
        ('general', _('عام')),
        ('account', _('الحساب')),
        ('jobs', _('الوظائف')),
        ('applications', _('التقديم')),
        ('employers', _('أصحاب العمل')),
        ('technical', _('تقني')),
        ('other', _('أخرى')),
    ]
    
    category = models.CharField(
        _("التصنيف"), 
        max_length=50, 
        choices=category_choices, 
        default='general'
    )
    
    # ✅ حالة السؤال
    is_active = models.BooleanField(_("نشط"), default=True)
    is_featured = models.BooleanField(_("مميز"), default=False)
    order = models.PositiveIntegerField(_("الترتيب"), default=0)
    views_count = models.PositiveIntegerField(_("عدد المشاهدات"), default=0)
    
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)
    
    class Meta:
        verbose_name = _("سؤال شائع")
        verbose_name_plural = _("الأسئلة الشائعة")
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['category']),
            models.Index(fields=['order']),
        ]
    
    def __str__(self):
        return self.question
    
    def increment_views(self):
        """زيادة عدد المشاهدات"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class Page(models.Model):
    """
    نموذج الصفحات الثابتة (من نحن، سياسة الخصوصية، الشروط...)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # ✅ معرف الصفحة (للاستخدام في URLs)
    slug = models.SlugField(
        _("الرابط المختصر"), 
        max_length=200, 
        unique=True,
        help_text=_("معرف فريد للصفحة - يستخدم في الرابط")
    )
    
    title = models.CharField(_("العنوان"), max_length=500)
    content = models.TextField(_("المحتوى"))
    
    meta_description = models.CharField(
        _("وصف SEO"), 
        max_length=500, 
        blank=True, 
        null=True
    )
    
    # ✅ الصور
    featured_image = models.ImageField(
        _("صورة مميزة"), 
        upload_to='pages/', 
        null=True, 
        blank=True
    )
    
    # ✅ حالة الصفحة
    is_active = models.BooleanField(_("نشط"), default=True)
    is_published = models.BooleanField(_("منشور"), default=True)
    published_at = models.DateTimeField(_("تاريخ النشر"), blank=True, null=True)
    
    # ✅ إعدادات العرض
    show_in_footer = models.BooleanField(_("عرض في التذييل"), default=False)
    show_in_header = models.BooleanField(_("عرض في الرأس"), default=False)
    order = models.PositiveIntegerField(_("الترتيب"), default=0)
    
    # ✅ إحصائيات
    views_count = models.PositiveIntegerField(_("عدد المشاهدات"), default=0)
    
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)
    created_by = models.CharField(_("تم الإنشاء بواسطة"), max_length=255, blank=True, null=True)
    
    class Meta:
        verbose_name = _("صفحة")
        verbose_name_plural = _("الصفحات")
        ordering = ['order', 'title']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_published']),
            models.Index(fields=['show_in_footer']),
            models.Index(fields=['show_in_header']),
            models.Index(fields=['order']),
        ]
    
    def __str__(self):
        return self.title
    
    def increment_views(self):
        """زيادة عدد المشاهدات"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def publish(self):
        """نشر الصفحة"""
        from django.utils import timezone
        self.is_published = True
        self.published_at = timezone.now()
        self.save(update_fields=['is_published', 'published_at'])


class SiteFeature(models.Model):
    """
    نموذج ميزات الموقع (للعرض في الصفحة الرئيسية)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    title = models.CharField(_("العنوان"), max_length=255)
    description = models.TextField(_("الوصف"))
    
    # ✅ الأيقونة
    icon = models.CharField(
        _("الأيقونة"), 
        max_length=100, 
        help_text=_("اسم أيقونة Font Awesome (مثال: fa-users)")
    )
    icon_color = models.CharField(
        _("لون الأيقونة"), 
        max_length=50, 
        default="text-blue-500",
        help_text=_("لون الأيقونة (مثال: text-blue-500, text-green-500)")
    )
    
    # ✅ حالة الميزة
    is_active = models.BooleanField(_("نشط"), default=True)
    order = models.PositiveIntegerField(_("الترتيب"), default=0)
    
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)
    
    class Meta:
        verbose_name = _("ميزة الموقع")
        verbose_name_plural = _("ميزات الموقع")
        ordering = ['order']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['order']),
        ]
    
    def __str__(self):
        return self.title