# core/urls.py
from django.urls import path
from . import views
from .views import *

app_name = 'core'


urlpatterns = [
    # الصفحات العامة
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('faq/', views.faq_view, name='faq'),
    path('search/', views.search_view, name='search'),
    path('page/<slug:slug>/', views.page_detail_view, name='page_detail'),
    
    # النشرة البريدية
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('newsletter/unsubscribe/<str:token>/', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
    path('newsletter/verify/<str:token>/', views.verify_newsletter, name='verify_newsletter'),
    
    # نماذج إضافية
    path('testimonial/submit/', views.submit_testimonial, name='submit_testimonial'),
    
    # APIs
    path('api/contact/', views.contact_api, name='contact_api'),
    path('api/newsletter/', views.newsletter_api, name='newsletter_api'),
]

# =================== Error Handlers ===================
handler400 = 'core.views.handler400'
handler403 = 'core.views.handler403'
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'