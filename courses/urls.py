from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import CustomLoginView

app_name = 'courses'

urlpatterns = [
    # ==================== Authentication ====================
    path('register/', views.register_view, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='courses:home'
    ), name='logout'),
    
    # ==================== Profile ====================
    path('profile/', views.profile_view, name='profile'),
    path('profile/update-avatar/', views.update_avatar, name='update_avatar'),

    # ==================== Courses ====================
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('course/<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    
    # ==================== Course Learning ====================
    path('course/<slug:slug>/learn/', views.course_learn_view, name='course_learn'),
    path('course/<slug:course_slug>/lesson/<int:lesson_id>/', views.lesson_view, name='lesson_view'),
    path('lesson/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    
    # ==================== User Actions ====================
    path('course/<slug:slug>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('course/<slug:slug>/review/', views.add_review, name='add_review'),
    path('course/<slug:slug>/enroll/', views.enroll_course, name='enroll'),  # أضف هذا السطر

    # ==================== Dashboards ====================
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/instructor/', views.instructor_dashboard, name='instructor_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # ==================== Admin: User Management ====================
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/create/', views.admin_user_create, name='admin_user_create'),
    path('admin/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin/users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('admin/users/<int:user_id>/toggle-active/', views.admin_user_toggle_active, name='admin_user_toggle_active'),
    path('admin/users/<int:user_id>/change-role/', views.admin_user_change_role, name='admin_user_change_role'),
    
    # ==================== Admin: Course Management ====================
    path('admin/courses/', views.admin_courses, name='admin_courses'),
    path('admin/courses/create/', views.admin_course_create, name='admin_course_create'),
    path('admin/courses/<int:course_id>/', views.admin_course_detail, name='admin_course_detail'),
    path('admin/courses/<int:course_id>/edit/', views.admin_course_edit, name='admin_course_edit'),
    path('admin/courses/<int:course_id>/delete/', views.admin_course_delete, name='admin_course_delete'),
    path('admin/courses/<int:course_id>/toggle-active/', views.admin_course_toggle_active, name='admin_course_toggle_active'),
    path('admin/courses/<int:course_id>/toggle-featured/', views.admin_course_toggle_featured, name='admin_course_toggle_featured'),
    
    # ==================== Admin: Module Management ====================
    path('admin/courses/<int:course_id>/modules/create/', views.admin_module_create, name='admin_module_create'),
    path('admin/modules/<int:module_id>/edit/', views.admin_module_edit, name='admin_module_edit'),
    path('admin/modules/<int:module_id>/delete/', views.admin_module_delete, name='admin_module_delete'),
    
    # ==================== Admin: Lesson Management ====================
    path('admin/modules/<int:module_id>/lessons/create/', views.admin_lesson_create, name='admin_lesson_create'),
    path('admin/lessons/<int:lesson_id>/edit/', views.admin_lesson_edit, name='admin_lesson_edit'),
    path('admin/lessons/<int:lesson_id>/delete/', views.admin_lesson_delete, name='admin_lesson_delete'),
    
    # ==================== Admin: Category Management ====================
    path('admin/categories/', views.admin_categories, name='admin_categories'),
    path('admin/categories/create/', views.admin_category_create, name='admin_category_create'),
    path('admin/categories/<int:category_id>/edit/', views.admin_category_edit, name='admin_category_edit'),
    path('admin/categories/<int:category_id>/delete/', views.admin_category_delete, name='admin_category_delete'),
    
    # ==================== Admin: Enrollment Management ====================
    path('admin/enrollments/', views.admin_enrollments, name='admin_enrollments'),
    path('admin/enrollments/create/', views.admin_enrollment_create, name='admin_enrollment_create'),
    path('admin/enrollments/<int:enrollment_id>/', views.admin_enrollment_detail, name='admin_enrollment_detail'),
    path('admin/enrollments/<int:enrollment_id>/update-status/', views.admin_enrollment_update_status, name='admin_enrollment_update_status'),
    path('admin/enrollments/<int:enrollment_id>/delete/', views.admin_enrollment_delete, name='admin_enrollment_delete'),
    
    # ==================== Admin: Review Management ====================
    path('admin/reviews/', views.admin_reviews, name='admin_reviews'),
    path('admin/reviews/<int:review_id>/delete/', views.admin_review_delete, name='admin_review_delete'),
    
    # ==================== Admin: Reports & Exports ====================
    path('admin/reports/', views.admin_reports, name='admin_reports'),
    path('admin/export/users/', views.admin_export_users, name='admin_export_users'),
    path('admin/export/courses/', views.admin_export_courses, name='admin_export_courses'),
    path('admin/export/enrollments/', views.admin_export_enrollments, name='admin_export_enrollments'),
    
    # ==================== AJAX Endpoints ====================
    path('ajax/toggle-favorite/', views.ajax_toggle_favorite, name='ajax_toggle_favorite'),
    path('ajax/update-lesson-progress/', views.ajax_update_lesson_progress, name='ajax_update_lesson_progress'),
    path('ajax/course-stats/<int:course_id>/', views.ajax_get_course_stats, name='ajax_get_course_stats'),
    path('ajax/dashboard-stats/', views.ajax_get_dashboard_stats, name='ajax_dashboard_stats'),
    path('ajax/chart-data/', views.ajax_get_chart_data, name='ajax_chart_data'),
    
    path('ajax/recent-activities/', views.ajax_get_recent_activities, name='ajax_recent_activities'),
    
    path('admin/stats/', views.admin_stats_view, name='admin_stats'),
    
    
    # ==================== Cart URLs ====================
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:course_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:course_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/submit-order/', views.submit_order, name='submit_order'),
    path('orders/', views.order_history, name='order_history'),

    # ==================== Instructor Public Profile ====================
    path('instructor/<int:instructor_id>/', views.instructor_profile, name='instructor_profile'),

]