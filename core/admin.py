# =========================
# core/admin.py - إدارة لوحة تحكم core
# =========================
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from import_export.admin import ImportExportModelAdmin
from .models import (
    SiteSettings, ContactMessage, NewsletterSubscriber,
    Testimonial, Partner, FAQ, Page, SiteFeature
)

# =========================
# ADMIN ACTIONS
# =========================
@admin.action(description='تفعيل العناصر المحددة')
def activate_items(modeladmin, request, queryset):
    count = queryset.update(is_active=True)
    messages.success(request, f'تم تفعيل {count} عنصر بنجاح')

@admin.action(description='إلغاء تفعيل العناصر المحددة')
def deactivate_items(modeladmin, request, queryset):
    count = queryset.update(is_active=False)
    messages.success(request, f'تم إلغاء تفعيل {count} عنصر بنجاح')

@admin.action(description='وضع علامة كمقروء')
def mark_as_read(modeladmin, request, queryset):
    queryset.update(is_read=True)
    messages.success(request, 'تم تحديث الحالة بنجاح')

@admin.action(description='وضع علامة كتم الرد')
def mark_as_replied(modeladmin, request, queryset):
    queryset.update(is_replied=True, replied_at=timezone.now())
    messages.success(request, 'تم تحديث الحالة بنجاح')

# =========================
# SITE SETTINGS ADMIN
# =========================
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'site_email', 'is_active', 'maintenance_mode', 'created_at_date']
    list_filter = ['is_active', 'maintenance_mode', 'created_at']
    search_fields = ['site_name', 'site_email']
    list_editable = ['is_active', 'maintenance_mode']
    
    fieldsets = (
        ('معلومات الموقع', {
            'fields': ('site_name', 'site_title', 'site_description', 'site_keywords')
        }),
        ('معلومات التواصل', {
            'fields': ('site_email', 'site_phone', 'site_whatsapp', 'site_address'),
            'classes': ('wide',),
        }),
        ('روابط التواصل الاجتماعي', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url', 'youtube_url'),
            'classes': ('collapse',),
        }),
        ('الشعارات والصور', {
            'fields': ('site_logo', 'site_logo_white', 'site_favicon', 'site_icon', 'site_og_image'),
            'classes': ('collapse',),
        }),
        ('إعدادات SEO', {
            'fields': ('meta_author', 'copyright_text', 'google_analytics_id', 'google_site_verification'),
            'classes': ('collapse',),
        }),
        ('إعدادات البريد الإلكتروني', {
            'fields': ('smtp_server', 'smtp_port', 'smtp_username', 'smtp_password', 'smtp_use_tls'),
            'classes': ('collapse',),
        }),
        ('حالة الموقع', {
            'fields': ('is_active', 'maintenance_mode'),
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def created_at_date(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_date.short_description = 'تاريخ الإنشاء'
    created_at_date.admin_order_field = 'created_at'
    
    actions = [activate_items, deactivate_items]

# =========================
# CONTACT MESSAGE ADMIN
# =========================
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'is_replied', 'created_at_date']
    list_filter = ['is_read', 'is_replied', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['is_read', 'is_replied']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('معلومات المرسل', {
            'fields': ('name', 'email', 'phone')
        }),
        ('الرسالة', {
            'fields': ('subject', 'message'),
        }),
        ('حالة الرسالة', {
            'fields': ('is_read', 'is_replied', 'replied_at', 'replied_by', 'reply_message'),
        }),
        ('معلومات إضافية', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',),
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'ip_address', 'user_agent']
    
    def created_at_date(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_date.short_description = 'تاريخ الإرسال'
    created_at_date.admin_order_field = 'created_at'
    
    actions = [mark_as_read, mark_as_replied]

# =========================
# NEWSLETTER SUBSCRIBER ADMIN
# =========================
@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'is_active', 'is_verified', 'created_at_date']
    list_filter = ['is_active', 'is_verified', 'receive_job_alerts', 'receive_newsletter', 'created_at']
    search_fields = ['email', 'name']
    list_editable = ['is_active', 'is_verified']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('معلومات المشترك', {
            'fields': ('email', 'name')
        }),
        ('حالة الاشتراك', {
            'fields': ('is_active', 'is_verified', 'verification_token', 'verified_at'),
        }),
        ('إعدادات الاشتراك', {
            'fields': ('receive_job_alerts', 'receive_newsletter'),
        }),
        ('معلومات إضافية', {
            'fields': ('ip_address', 'unsubscribed_at'),
            'classes': ('collapse',),
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'verification_token']
    
    def created_at_date(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_date.short_description = 'تاريخ الاشتراك'
    created_at_date.admin_order_field = 'created_at'
    
    actions = ['verify_selected', 'unsubscribe_selected']
    
    @admin.action(description='توثيق المشتركين المحددين')
    def verify_selected(modeladmin, request, queryset):
        for sub in queryset:
            sub.verify()
        messages.success(request, f'تم توثيق {queryset.count()} مشترك')
    
    @admin.action(description='إلغاء اشتراك المحددين')
    def unsubscribe_selected(modeladmin, request, queryset):
        for sub in queryset:
            sub.unsubscribe()
        messages.success(request, f'تم إلغاء اشتراك {queryset.count()} مشترك')

# =========================
# TESTIMONIAL ADMIN
# =========================
@admin.register(Testimonial)
class TestimonialAdmin(ImportExportModelAdmin):
    list_display = ['name', 'company', 'rating_display', 'is_active', 'is_featured', 'order']
    list_filter = ['is_active', 'is_featured', 'rating', 'created_at']
    search_fields = ['name', 'company', 'content']
    list_editable = ['is_active', 'is_featured', 'order']
    
    fieldsets = (
        ('معلومات العميل', {
            'fields': ('name', 'position', 'company')
        }),
        ('الشهادة', {
            'fields': ('content', 'rating'),
        }),
        ('الصور', {
            'fields': ('avatar', 'company_logo'),
            'classes': ('wide',),
        }),
        ('حالة الشهادة', {
            'fields': ('is_active', 'is_featured', 'order'),
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def rating_display(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html(
            '<span style="color: #fbbf24;">{}</span>',
            stars
        )
    rating_display.short_description = 'التقييم'
    
    actions = [activate_items, deactivate_items]

# =========================
# PARTNER ADMIN
# =========================
@admin.register(Partner)
class PartnerAdmin(ImportExportModelAdmin):
    list_display = ['name', 'logo_preview', 'website_url', 'is_active', 'is_featured', 'order']
    list_filter = ['is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'is_featured', 'order']
    
    fieldsets = (
        ('معلومات الشريك', {
            'fields': ('name', 'description', 'website_url')
        }),
        ('الشعار', {
            'fields': ('logo',),
        }),
        ('حالة الشريك', {
            'fields': ('is_active', 'is_featured', 'order'),
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'logo_preview']
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.logo.url)
        return 'لا يوجد شعار'
    logo_preview.short_description = 'معاينة الشعار'
    
    actions = [activate_items, deactivate_items]

# =========================
# FAQ ADMIN
# =========================
@admin.register(FAQ)
class FAQAdmin(ImportExportModelAdmin):
    list_display = ['question_short', 'category', 'views_count', 'is_active', 'is_featured', 'order']
    list_filter = ['category', 'is_active', 'is_featured', 'created_at']
    search_fields = ['question', 'answer']
    list_editable = ['is_active', 'is_featured', 'order']
    
    fieldsets = (
        ('السؤال والإجابة', {
            'fields': ('question', 'answer')
        }),
        ('التصنيف', {
            'fields': ('category',),
        }),
        ('حالة السؤال', {
            'fields': ('is_active', 'is_featured', 'order', 'views_count'),
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    
    def question_short(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_short.short_description = 'السؤال'
    
    actions = [activate_items, deactivate_items]

# =========================
# PAGE ADMIN
# =========================
@admin.register(Page)
class PageAdmin(ImportExportModelAdmin):
    list_display = ['title', 'slug', 'is_published', 'show_in_header', 'show_in_footer', 'views_count', 'order']
    list_filter = ['is_active', 'is_published', 'show_in_header', 'show_in_footer', 'created_at']
    search_fields = ['title', 'content', 'slug']
    list_editable = ['is_published', 'show_in_header', 'show_in_footer', 'order']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('معلومات الصفحة', {
            'fields': ('title', 'slug', 'featured_image')
        }),
        ('المحتوى', {
            'fields': ('content',),
            'classes': ('wide',),
        }),
        ('تحسين محركات البحث SEO', {
            'fields': ('meta_description',),
            'classes': ('collapse',),
        }),
        ('إعدادات العرض', {
            'fields': ('is_active', 'is_published', 'published_at', 'show_in_header', 'show_in_footer', 'order'),
        }),
        ('إحصائيات', {
            'fields': ('views_count',),
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    
    actions = ['publish_pages', 'unpublish_pages']
    
    @admin.action(description='نشر الصفحات المحددة')
    def publish_pages(modeladmin, request, queryset):
        for page in queryset:
            page.publish()
        messages.success(request, f'تم نشر {queryset.count()} صفحة')
    
    @admin.action(description='إلغاء نشر الصفحات المحددة')
    def unpublish_pages(modeladmin, request, queryset):
        queryset.update(is_published=False)
        messages.success(request, f'تم إلغاء نشر {queryset.count()} صفحة')

# =========================
# SITE FEATURE ADMIN
# =========================
@admin.register(SiteFeature)
class SiteFeatureAdmin(ImportExportModelAdmin):
    list_display = ['title', 'icon_display', 'is_active', 'order']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['is_active', 'order']
    
    fieldsets = (
        ('معلومات الميزة', {
            'fields': ('title', 'description')
        }),
        ('الأيقونة', {
            'fields': ('icon', 'icon_color'),
            'help_texts': {
                'icon': 'اسم أيقونة Font Awesome (مثال: fa-users)',
                'icon_color': 'لون الأيقونة (مثال: text-blue-500)'
            }
        }),
        ('حالة الميزة', {
            'fields': ('is_active', 'order'),
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def icon_display(self, obj):
        return format_html(
            '<i class="fas {}" style="color: {}; font-size: 1.2rem;"></i>',
            obj.icon,
            obj.icon_color.replace('text-', '#') if 'text-' in obj.icon_color else obj.icon_color
        )
    icon_display.short_description = 'الأيقونة'
    
    actions = [activate_items, deactivate_items]