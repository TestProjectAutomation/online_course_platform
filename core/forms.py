from django import forms
from django.contrib.auth.forms import *
from .models import ContactMessage, NewsletterSubscriber, Testimonial
from django import forms
from django.contrib.auth.forms import *
from .models import (
    SiteSettings, ContactMessage, NewsletterSubscriber, 
    Testimonial, FAQ, Page, SiteFeature, Partner
)
# تعريف كلاسات CSS للتيلويند
TAILWIND_INPUT = "w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition"
TAILWIND_TEXTAREA = "w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition resize-y"
TAILWIND_SELECT = "w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition"
TAILWIND_CHECKBOX = "w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
TAILWIND_RADIO = "w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
TAILWIND_FILE = "block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400"


class ContactForm(forms.Form):
    """نموذج الاتصال"""
    name = forms.CharField(
        max_length=100,
        label="الاسم الكامل",
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'أدخل اسمك الكامل',
            'required': True
        })
    )
    email = forms.EmailField(
        label="البريد الإلكتروني",
        widget=forms.EmailInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'example@domain.com',
            'required': True,
            'dir': 'ltr'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        label="رقم الهاتف (اختياري)",
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': '+20 123 456 789',
            'dir': 'ltr'
        })
    )
    subject = forms.CharField(
        max_length=200,
        label="الموضوع",
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'موضوع الرسالة',
            'required': True
        })
    )
    message = forms.CharField(
        label="الرسالة",
        widget=forms.Textarea(attrs={
            'class': TAILWIND_TEXTAREA,
            'rows': 5,
            'placeholder': 'اكتب رسالتك هنا...',
            'required': True
        })
    )
    
    def clean_email(self):
        """التحقق من صحة البريد الإلكتروني"""
        email = self.cleaned_data.get('email')
        if email:
            # التحقق من النطاق
            allowed_domains = ['.com', '.net', '.org', '.sa', '.eg', '.ae']
            if not any(email.lower().endswith(domain) for domain in allowed_domains):
                raise forms.ValidationError('يرجى إدخال بريد إلكتروني صحيح (مثل: .com, .net, .org)')
        return email
    
    def clean_phone(self):
        """تنسيق رقم الهاتف"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # إزالة المسافات والرموز غير الرقمية
            import re
            phone = re.sub(r'[^\d+]', '', phone)
            if len(phone) < 10:
                raise forms.ValidationError('رقم الهاتف يجب أن يكون 10 أرقام على الأقل')
        return phone


class NewsletterForm(forms.Form):
    """نموذج الاشتراك في النشرة البريدية"""
    name = forms.CharField(
        max_length=100,
        required=False,
        label="الاسم (اختياري)",
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'الاسم (اختياري)'
        })
    )
    email = forms.EmailField(
        label="البريد الإلكتروني",
        widget=forms.EmailInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'example@domain.com',
            'required': True,
            'dir': 'ltr'
        })
    )
    
    def clean_email(self):
        """التحقق من عدم وجود اشتراك سابق"""
        email = self.cleaned_data.get('email')
        if email:
            # التحقق من صحة البريد
            if NewsletterSubscriber.objects.filter(email=email, is_active=True).exists():
                raise forms.ValidationError('هذا البريد مسجل بالفعل في النشرة البريدية')
        return email


class SubscriberForm(forms.ModelForm):
    """نموذج المشتركين (للواجهة الإدارية)"""
    class Meta:
        model = NewsletterSubscriber
        fields = ['email', 'name', 'is_active', 'is_verified', 'receive_job_alerts', 'receive_newsletter']
        widgets = {
            'email': forms.EmailInput(attrs={'class': TAILWIND_INPUT, 'dir': 'ltr'}),
            'name': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'is_active': forms.CheckboxInput(attrs={'class': TAILWIND_CHECKBOX}),
            'is_verified': forms.CheckboxInput(attrs={'class': TAILWIND_CHECKBOX}),
            'receive_job_alerts': forms.CheckboxInput(attrs={'class': TAILWIND_CHECKBOX}),
            'receive_newsletter': forms.CheckboxInput(attrs={'class': TAILWIND_CHECKBOX}),
        }


class TestimonialForm(forms.ModelForm):
    """نموذج إضافة شهادة عميل"""
    class Meta:
        model = Testimonial
        fields = ['name', 'position', 'company', 'content', 'rating', 'avatar', 'company_logo']
        widgets = {
            'name': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'الاسم الكامل'}),
            'position': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'المسمى الوظيفي'}),
            'company': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'اسم الشركة'}),
            'content': forms.Textarea(attrs={'class': TAILWIND_TEXTAREA, 'rows': 4, 'placeholder': 'نص الشهادة'}),
            'rating': forms.Select(attrs={'class': TAILWIND_SELECT}),
            'avatar': forms.FileInput(attrs={'class': TAILWIND_FILE}),
            'company_logo': forms.FileInput(attrs={'class': TAILWIND_FILE}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].choices = [(i, f'{i} نجوم') for i in range(1, 6)]


class SearchForm(forms.Form):
    """نموذج البحث"""
    q = forms.CharField(
        required=False,
        label="بحث",
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'ابحث عن دورات، مقالات، أسئلة...'
        })
    )
    category = forms.ChoiceField(
        required=False,
        label="التصنيف",
        widget=forms.Select(attrs={'class': TAILWIND_SELECT})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # إضافة خيارات التصنيف ديناميكياً
        categories = [('', 'الكل')]
        try:
            from .models import FAQ
            for code, name in FAQ.category_choices:
                categories.append((code, name))
        except:
            pass
        self.fields['category'].choices = categories


class SiteSettingsForm(forms.ModelForm):
    """نموذج إعدادات الموقع (للواجهة الإدارية)"""
    class Meta:
        model = SiteSettings
        exclude = ['id', 'created_at', 'updated_at']
        widgets = {
            'site_name': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'site_title': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'site_description': forms.Textarea(attrs={'class': TAILWIND_TEXTAREA, 'rows': 3}),
            'site_keywords': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'site_email': forms.EmailInput(attrs={'class': TAILWIND_INPUT, 'dir': 'ltr'}),
            'site_phone': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'dir': 'ltr'}),
            'site_whatsapp': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'dir': 'ltr'}),
            'site_address': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'facebook_url': forms.URLInput(attrs={'class': TAILWIND_INPUT, 'dir': 'ltr'}),
            'twitter_url': forms.URLInput(attrs={'class': TAILWIND_INPUT, 'dir': 'ltr'}),
            'instagram_url': forms.URLInput(attrs={'class': TAILWIND_INPUT, 'dir': 'ltr'}),
            'linkedin_url': forms.URLInput(attrs={'class': TAILWIND_INPUT, 'dir': 'ltr'}),
            'youtube_url': forms.URLInput(attrs={'class': TAILWIND_INPUT, 'dir': 'ltr'}),
            'site_logo': forms.FileInput(attrs={'class': TAILWIND_FILE}),
            'site_favicon': forms.FileInput(attrs={'class': TAILWIND_FILE}),
            'copyright_text': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'google_analytics_id': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'dir': 'ltr'}),
            'smtp_server': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'dir': 'ltr'}),
            'smtp_port': forms.NumberInput(attrs={'class': TAILWIND_INPUT, 'dir': 'ltr'}),
            'smtp_username': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'dir': 'ltr'}),
            'smtp_password': forms.PasswordInput(attrs={'class': TAILWIND_INPUT, 'dir': 'ltr'}),
            'smtp_use_tls': forms.CheckboxInput(attrs={'class': TAILWIND_CHECKBOX}),
            'is_active': forms.CheckboxInput(attrs={'class': TAILWIND_CHECKBOX}),
            'maintenance_mode': forms.CheckboxInput(attrs={'class': TAILWIND_CHECKBOX}),
        }


class ContactMessageForm(forms.ModelForm):
    """نموذج رسائل التواصل (للواجهة الإدارية)"""
    class Meta:
        model = ContactMessage
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'email': forms.EmailInput(attrs={'class': TAILWIND_INPUT, 'dir': 'ltr'}),
            'phone': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'dir': 'ltr'}),
            'subject': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'message': forms.Textarea(attrs={'class': TAILWIND_TEXTAREA, 'rows': 4}),
            'reply_message': forms.Textarea(attrs={'class': TAILWIND_TEXTAREA, 'rows': 4}),
            'is_read': forms.CheckboxInput(attrs={'class': TAILWIND_CHECKBOX}),
            'is_replied': forms.CheckboxInput(attrs={'class': TAILWIND_CHECKBOX}),
            'replied_by': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
        }


class PageForm(forms.ModelForm):
    """نموذج الصفحات الثابتة"""
    class Meta:
        model = Page
        fields = ['title', 'slug', 'content', 'meta_description', 'featured_image', 
                  'is_active', 'is_published', 'show_in_header', 'show_in_footer', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'slug': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'dir': 'ltr'}),
            'content': forms.Textarea(attrs={'class': TAILWIND_TEXTAREA, 'rows': 10}),
            'meta_description': forms.Textarea(attrs={'class': TAILWIND_TEXTAREA, 'rows': 3}),
            'featured_image': forms.FileInput(attrs={'class': TAILWIND_FILE}),
            'is_active': forms.CheckboxInput(attrs={'class': TAILWIND_CHECKBOX}),
            'is_published': forms.CheckboxInput(attrs={'class': TAILWIND_CHECKBOX}),
            'show_in_header': forms.CheckboxInput(attrs={'class': TAILWIND_CHECKBOX}),
            'show_in_footer': forms.CheckboxInput(attrs={'class': TAILWIND_CHECKBOX}),
            'order': forms.NumberInput(attrs={'class': TAILWIND_INPUT}),
        }