from django.urls import path
from . import views

urlpatterns = [
    # user-facing
    path('', views.activity_list, name='activity_list'),
    path('activity/<int:activity_id>/enroll/', views.enroll, name='enroll'),
    path('activity/<int:activity_id>/unenroll/', views.unenroll, name='unenroll'),
    path('my-score/', views.my_score, name='my_score'),

    path('activity/<int:activity_id>/', views.activity_details, name='activity_details'),
    path('calendar/', views.calendar, name='calendar'),

    # our own admin panel (staff only)
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/activities/new/', views.admin_activity_create, name='admin_activity_create'),
    path('admin-panel/activities/<int:activity_id>/edit/', views.admin_activity_edit, name='admin_activity_edit'),
    path('admin-panel/activities/<int:activity_id>/delete/', views.admin_activity_delete, name='admin_activity_delete'),
    path('admin-panel/accounts/', views.admin_account_list, name='admin_account_list'),
    path('admin-panel/accounts/new/', views.admin_account_create, name='admin_account_create'),
    path('admin-panel/accounts/<int:user_id>/', views.admin_account_detail, name='admin_account_detail'),
    path('admin-panel/accounts/<int:user_id>/delete/', views.admin_account_delete, name='admin_account_delete'),
]