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
    ALLOWED_HOSTS += ['127.0.0.1', 'localhost', 'c3gwhgm0-5000.uks1.devtunnels.ms']


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
    # 'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rangefilter',
    'import_export',

    'courses',
    'core',
    'notifications',
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
                
                
                # Custom context processors
                'core.context_processors.site_settings',  # استبدل core باسم تطبيقك
                'core.context_processors.contact_info',
                'core.context_processors.social_links',
                'core.context_processors.meta_tags',
                'core.context_processors.breadcrumbs',
                'core.context_processors.notifications',
                'core.context_processors.cart_info',
                'core.context_processors.current_year',
                'core.context_processors.is_mobile',
                
                'notifications.context_processors.notifications_processor',

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

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

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







# # =========================
# # Jazzmin - إعدادات محسنة للعربية مع دعم RTL
# # =========================


# JAZZMIN_SETTINGS = {
#     "site_title": "My Site",
#     "site_header": "My Site",
#     "site_brand": "My Site",
#     "site_logo": "images/logo.png",
#     "site_logo_classes": "img-circle",
#     "welcome_sign": "Welcome to My Site",
#     "copyright": "My Site",
#     "search_model": ["auth.User", "auth.Group"],
#     "user_avatar": None,

#     "topmenu_links": [
#         {"name": "Home", "url": "admin:dashboard", "permissions": ["auth.view_user"]},
#         {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
#         {"model": "auth.user"},
#     ],
#     "usermenu_links": [
#         {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
#         {"model": "auth.user"},
#     ],
#     "show_ui_builder": True,
#     "changeform_format": "horizontal_tabs",
#     "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
#     "language_chooser": True,
# }
