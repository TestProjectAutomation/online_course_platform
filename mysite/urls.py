from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # لوحة تحكم Django Admin
    path('admin-panel/', admin.site.urls),
    
    # تطبيق الدورات (جميع مسارات التطبيق)
    path('', include('courses.urls')),
    
    # إعادة توجيه الصفحة الرئيسية
    path('home/', RedirectView.as_view(url='/', permanent=True)),
]

# خدمة الملفات في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)