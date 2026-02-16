import os
from pathlib import Path
from decouple import config
from django.utils.translation import gettext_lazy as _
from django.contrib.messages import constants as messages
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.messages import constants as messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# BASE & SECURITY
# =========================

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('MY_DEBUG', default=False, cast=bool)


if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_SSL_REDIRECT = True



USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = not DEBUG


MAIN_DOMAIN = config('MAIN_DOMAIN', default='nextjobs.deplois.net').replace('https://', '').replace('http://', '')


ALLOWED_HOSTS = [MAIN_DOMAIN, f'www.{MAIN_DOMAIN}']
if DEBUG:
    ALLOWED_HOSTS += ['127.0.0.1', 'localhost']


CSRF_TRUSTED_ORIGINS = [
    f'https://{MAIN_DOMAIN}',
    f'https://www.{MAIN_DOMAIN}',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


if DEBUG:
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
else:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True



INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'courses',
]




SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]




ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # إضافة context_processors الخاصة بك
                'courses.context_processors.site_settings',
                'courses.context_processors.categories_processor',
                'courses.context_processors.featured_courses_processor',
                'courses.context_processors.user_data_processor',
                'courses.context_processors.stats_processor',
                'courses.context_processors.breadcrumbs_processor',
                'courses.context_processors.cart_processor',

            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'


# =========================
# DATABASE
# =========================
if LOCAL := config('LOCAL', default=True, cast=bool):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': config('DB_ENGINE'),
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT', cast=int),
        }
    }
    
    
    
    
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ar-eg'
TIME_ZONE = 'Africa/Cairo'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('ar', _('العربية')),
    ('en', _('English')),
]

LANGUAGE_CODE = 'ar'

USE_I18N = True
USE_L10N = True

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]



STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'courses.User'

LOGIN_URL = 'admin:login'


LOGIN_URL = 'courses:login'
LOGIN_REDIRECT_URL = 'courses:user_dashboard'
LOGOUT_REDIRECT_URL = 'courses:home'



# WhatsApp Settings
WHATSAPP_NUMBER = config('WHATSAPP_NUMBER', default='201234567890')

# Email Settings (for production)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'



# =========================
# STATIC & MEDIA
# =========================
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    '/usr/src/app/static/',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# إعدادات crispy forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'







# =========================
# Jazzmin - إعدادات محسنة للعربية مع دعم RTL
# =========================

JAZZMIN_SETTINGS = {
    # المعلومات الأساسية
    'site_title': 'منصة التعلم - لوحة التحكم',
    'site_header': 'منصة التعلم',
    'site_brand': 'منصة التعلم',
    'site_logo': None,  # يمكنك إضافة شعار هنا: 'images/logo.png'
    'site_logo_classes': 'img-circle',
    'site_icon': None,
    
    # ترحيب وحقوق
    'welcome_sign': 'مرحباً بك في لوحة تحكم منصة التعلم',
    'copyright': f'جميع الحقوق محفوظة © منصة التعلم {timezone.now().year}',
    
    # المستخدم والصورة
    'user_avatar': 'avatar',  # اسم حقل الصورة في نموذج User
    
    # إعدادات البحث
    'search_model': [
        'courses.Course', 
        'courses.User', 
        'courses.Category',
        'courses.Lesson'
    ],
    
    # الشريط العلوي - روابط
    'topmenu_links': [
        # عنوان الصفحة الرئيسية
        {'name': 'الرئيسية', 'url': 'admin:index', 'permissions': ['auth.view_user']},
        
        # رابط العودة للموقع
        {'name': 'عرض الموقع', 'url': '/', 'new_window': True},
        
        # روابط للتطبيقات المهمة
        {'app': 'courses'},
        
        # قائمة المستخدمين
        {'model': 'courses.User'},
        
        # روابط مخصصة
        {'name': 'الدعم الفني', 'url': '/admin/support/', 'new_window': True},
    ],
    
    # روابط مفيدة في الشريط الجانبي
    'useful_links': {
        'منصة التعلم': '/',
        'توثيق Django': 'https://docs.djangoproject.com/',
        'جيت هاب': 'https://github.com/',
    },
    
    # إعدادات القوائم الجانبية
    'show_sidebar': True,
    'navigation_expanded': True,
    'hide_apps': [],
    'hide_models': [],
    
    # ترتيب التطبيقات في القائمة الجانبية
    'order_with_respect_to': [
        'courses',  # تطبيق الدورات أولاً
        'courses.Course',
        'courses.Category',
        'courses.CourseModule',
        'courses.Lesson',
        'courses.User',
        'courses.Enrollment',
        'courses.Review',
        'courses.Favorite',
        'auth',     # ثم تطبيق المصادقة
        'auth.User',
        'auth.Group',
    ],
    
    # أيقونات للتطبيقات والنماذج (باستخدام Font Awesome 5)
    'icons': {
        # تطبيق courses
        'courses': 'fas fa-graduation-cap',
        'courses.Course': 'fas fa-book-open',
        'courses.Category': 'fas fa-folder-tree',
        'courses.CourseModule': 'fas fa-cubes',
        'courses.Lesson': 'fas fa-video',
        'courses.User': 'fas fa-user-circle',
        'courses.Enrollment': 'fas fa-user-graduate',
        'courses.Review': 'fas fa-star',
        'courses.Favorite': 'fas fa-heart',
        
        # تطبيق auth
        'auth': 'fas fa-users-cog',
        'auth.User': 'fas fa-user',
        'auth.Group': 'fas fa-users',
    },
    
    # أيقونات افتراضية
    'default_icon_parents': 'fas fa-folder',
    'default_icon_children': 'fas fa-file',
    
    # إعدادات نماذج التغيير
    'changeform_format': 'horizontal_tabs',
    'changeform_format_overrides': {
        'courses.User': 'collapsible',
        'auth.User': 'collapsible',
        'courses.Course': 'vertical_tabs',
        'courses.Category': 'vertical_tabs',
    },
    
    # إعدادات اللغة
    'language_chooser': True,  # إظهار قائمة اختيار اللغة
    
    # دعم النوافذ المنبثقة
    'related_modal_active': True,
    
    # روابط مخصصة في شريط الأدوات
    'custom_links': {
        'courses': [{
            'name': 'إحصائيات سريعة',
            'url': '/admin/stats/',
            'icon': 'fas fa-chart-pie',
            'permissions': ['courses.view_course']
        }]
    },
    
    # CSS و JS مخصص
    'custom_css': 'css/admin_custom.css',  # سنقوم بإنشائه
    'custom_js': 'js/admin_custom.js',      # سنقوم بإنشائه
    
    # إظهار/إخفاء مصمم الواجهة
    'show_ui_builder': True,
}

# =========================
# Jazzmin UI Tweaks - إعدادات الواجهة
# =========================

JAZZMIN_UI_TWEAKS = {
    # سمة Bootstrap - نختار سمات تدعم RTL بشكل جيد
    'theme': 'flatly',  # أو 'cosmo', 'litera', 'minty', 'sandstone'
    
    # سمة الوضع الليلي
    'dark_mode_theme': 'darkly',  # 'cyborg', 'vapor', 'superhero'
    
    # إعدادات الشريط العلوي (Navbar)
    'navbar': 'navbar-dark',  # 'navbar-dark', 'navbar-light'
    'navbar_fixed': True,
    'navbar_small_text': False,
    'navbar_expanded': True,
    'brand_colour': 'navbar-primary',  # أو 'navbar-success', 'navbar-danger'
    'no_navbar_border': False,
    
    # إعدادات الشريط الجانبي (Sidebar)
    'sidebar': 'sidebar-dark-primary',  # 'sidebar-light-primary', 'sidebar-dark-warning'
    'sidebar_fixed': True,
    'sidebar_small_text': False,
    'sidebar_nav_small_text': False,
    'sidebar_disable_expand': False,
    'sidebar_nav_child_indent': True,
    'sidebar_nav_compact_style': False,
    'sidebar_nav_legacy_style': False,
    'sidebar_nav_flat_style': True,
    
    # إعدادات التذييل (Footer)
    'footer_fixed': False,
    'footer_small_text': False,
    
    # إعدادات النص العام
    'body_small_text': False,
    'brand_small_text': False,
    
    # الألوان المميزة
    'accent': 'accent-primary',  # 'accent-info', 'accent-success'
    
    # ألوان الأزرار
    'button_classes': {
        'primary': 'btn-primary',
        'secondary': 'btn-secondary',
        'info': 'btn-info',
        'warning': 'btn-warning',
        'danger': 'btn-danger',
        'success': 'btn-success',
        'outline-primary': 'btn-outline-primary',
        'outline-secondary': 'btn-outline-secondary',
        'outline-info': 'btn-outline-info',
        'outline-warning': 'btn-outline-warning',
        'outline-danger': 'btn-outline-danger',
        'outline-success': 'btn-outline-success',
    },
    
    # تأثيرات إضافية
    'actions_sticky_top': True,
}