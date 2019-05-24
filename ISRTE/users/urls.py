from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login_url'),
    path('logout/', views.logout_view, name='logout_url'),
    path('profile/<int:pk>', views.user_profile, name='user_profile_url'),
    path('', views.users_list, name='users_list_url'),
    path('groups/', views.group_list, name='group_list_url')
]
