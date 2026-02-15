import os
from pathlib import Path
from decouple import config
from django.utils.translation import gettext_lazy as _
from django.contrib.messages import constants as messages


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

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'courses.User'

LOGIN_URL = 'admin:login'
LOGIN_REDIRECT_URL = 'user_dashboard'

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









JAZZMIN_UI_TWEAKS = {
    # الألوان والسمات
    'theme': 'darkly',  # أو 'simplex', 'flatly', 'materia' - هذه السمات تدعم العربية بشكل أفضل
    'dark_mode_theme': 'darkly',
    
    # الشريط العلوي (Navbar)
    'navbar': 'navbar-dark',
    'navbar_fixed': True,
    'navbar_small_text': False,
    'brand_colour': 'navbar-primary',
    'no_navbar_border': True,
    
    # الشريط الجانبي (Sidebar)
    'sidebar': 'sidebar-dark-primary',
    'sidebar_fixed': True,
    'sidebar_nav_small_text': False,
    'sidebar_disable_expand': False,
    'sidebar_nav_child_indent': True,
    'sidebar_nav_compact_style': False,
    'sidebar_nav_legacy_style': False,
    'sidebar_nav_flat_style': False,
    
    # التذييل (Footer)
    'footer_fixed': False,
    'footer_small_text': False,
    
    # النص العام
    'body_small_text': False,
    'brand_small_text': False,
    
    # الألوان المميزة
    'accent': 'accent-primary',
    
    # الأزرار
    'button_classes': {
        'primary': 'btn-primary',
        'secondary': 'btn-secondary',
        'info': 'btn-info',
        'warning': 'btn-warning',
        'danger': 'btn-danger',
        'success': 'btn-success',
        'outline-primary': 'btn-outline-primary',
        'outline-secondary': 'btn-outline-secondary',
    },
    
    # تأثيرات إضافية
    'actions_sticky_top': True,
}

# =========================
# Jazzmin - إعدادات محسنة للعربية
# =========================

JAZZMIN_SETTINGS = {
    # المعلومات الأساسية
    'site_title': 'تالينت فلو - لوحة التحكم',
    'site_header': 'تالينت فلو',
    'site_brand': 'تالينت فلو',
    'site_logo': None,  # يمكنك إضافة شعار هنا
    'site_logo_classes': 'img-circle',
    'welcome_sign': 'مرحباً بك في لوحة تحكم تالينت فلو',
    'copyright': 'جميع الحقوق محفوظة © تالينت فلو 2026',
    
    # البحث
    'search_model': ['blog.Post', 'blog.Category'],
    
    # المستخدمون
    'user_avatar': None,
    'show_sidebar': True,
    'navigation_expanded': True,
    
    # اللغة والترجمة
    'language_chooser': True,
    
    # القوائم العلوية
    'topmenu_links': [
        {'name': 'الرئيسية', 'url': 'admin:index', 'permissions': ['auth.view_user']},
        {'name': 'عرض الموقع', 'url': '/', 'new_window': True},
        {'model': 'auth.User'},
        {'app': 'blog'},
        {'app': 'pages'},
    ],
    
    # الأيقونات
    'icons': {
        'auth': 'fas fa-users-cog',
        'auth.user': 'fas fa-user',
        'auth.Group': 'fas fa-users',
        'blog.Category': 'fas fa-tags',
        'blog.Post': 'fas fa-newspaper',
        'blog.Tag': 'fas fa-hashtag',
        'pages.Page': 'fas fa-file-alt',
        'account': 'fas fa-user-circle',
        'socialaccount': 'fas fa-share-alt',
        'sites': 'fas fa-globe',
    },
    
    'default_icon_parents': 'fas fa-chevron-circle-right',
    'default_icon_children': 'fas fa-dot-circle',
    
    # تخصيص القوائم الجانبية
    'order_with_respect_to': [
        'blog',
        'blog.Post',
        'blog.Category',
        'pages',
        'auth',
    ],
    
    # روابط مفيدة
    'useful_links': {
        'مستندات Django': 'https://docs.djangoproject.com/en/stable/',
        'مستندات Jazzmin': 'https://django-jazzmin.readthedocs.io/',
        'الدعم الفني': '/admin/support/',
    },
    
    # إجراءات مخصصة
    'custom_css': None,  # يمكنك إضافة CSS مخصص هنا
    'custom_js': None,   # يمكنك إضافة JS مخصص هنا
    
    # إظهار/إخفاء العناصر
    'show_ui_builder': True,  # يسمح بتخصيص الواجهة من لوحة التحكم
    
    # تغيير موقع القائمة الجانبية
    'changeform_format': 'horizontal_tabs',
    'changeform_format_overrides': {
        'auth.user': 'collapsible',
        'auth.group': 'vertical_tabs',
    },
    
    # دعم RTL (من اليمين لليسار)
    'related_modal_active': True,
}
