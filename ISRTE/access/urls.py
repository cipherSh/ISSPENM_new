from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.access_list, name='control_access_url'),
    path('group/<int:pk>/', views.GroupAccessUpdate.as_view(), name='group_access_update_url'),
    path('group/<int:pk>/delete/', views.group_access_delete, name='group_access_delete_url'),
    path('person/<int:pk>/', views.PersonalAccessUpdate.as_view(), name='personal_access_update_url'),
    path('person/<int:pk>/delete/', views.personal_access_delete, name='personal_access_delete_url'),
    path('request/<int:pk>/accept/', views.RequestToOpenAccept.as_view(), name='request_accept_url'),
    path('request/<int:pk>/accept/group/', views.RequestToOpenGroupAccept.as_view(), name='group_request_accept_url'),
    path('request/<int:pk>/reject/', views.RequestToOpenReject.as_view(), name='request_reject_url'),

]