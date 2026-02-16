from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # هذا يضيف مسار set_language

    # لوحة تحكم Django Admin
    path('admin-panel/', admin.site.urls),
    
    # تطبيق الدورات (جميع مسارات التطبيق)
    path('', include('courses.urls')),
    path('', include('core.urls')),

    # إعادة توجيه الصفحة الرئيسية
    path('home/', RedirectView.as_view(url='/', permanent=True)),
]

# خدمة الملفات في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)