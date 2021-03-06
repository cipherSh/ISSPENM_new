from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login_url'),
    path('logout/', views.logout_view, name='logout_url'),

    path('create/', views.user_create, name='user_create_url'),
    path('profile/<int:pk>', views.user_profile, name='user_profile_url'),
    path('profile/<int:pk>/logs/', views.profile_logs, name='profile_logs_url'),
    path('profile/<int:pk>/acts/', views.user_acts, name='user_acts_url'),
    path('profile/pass_edit/', views.password_edit, name='user_password_edit'),
    path('profile/<int:pk>/active/', views.inactive_user, name='user_active_url'),

    path('profile/<int:pk>/update/', views.UserUpdateView.as_view(), name='user_update_url'),
    path('profile/<int:pk>/delete/', views.user_delete, name='user_delete_url'),
    path('change/initial_pass/', views.change_initial_pass, name='change_initial_pass_url'),

    path('audit/', views.users_audit, name='users_audit_url'),
    path('logs/', views.users_logs, name='users_logs_url'),
    path('pdf/', views.some_view, name='pdf_url'),
    path('groups/', views.group_list, name='group_list_url'),
    path('', views.users_list, name='users_list_url'),
]
