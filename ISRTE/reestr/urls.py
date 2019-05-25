from django.urls import path, include
from . import views
from access.views import GroupAccessCreate, PersonalAccessCreate

urlpatterns = [
    path('', views.homepage, name='homepage_url'),
    path('registry/', views.registry_page, name='registry_url'),

    path('registry/criminals/', views.criminals_list, name='criminals_list_url'),
    path('registry/criminals/create/', views.CriminalCreateView.as_view(), name='criminal_create_url'),

    path('registry/criminal/<int:pk>', views.criminal_detail, name="criminal_detail_url"),
    path('registry/criminal/<int:pk>/update/', views.CriminalUpdateView.as_view(), name="criminal_update_url"),
    path('registry/criminal/<int:pk>/delete/', views.CriminalDeleteView.as_view(), name="criminal_delete_url"),

    path('registry/criminal/<int:pk>/access/group/create/', GroupAccessCreate.as_view(),
         name="group_access_create_url"),
    path('registry/criminal/<int:pk>/access/personal/create/', PersonalAccessCreate.as_view(),
         name="personal_access_create_url"),

    path('registry/criminal/<int:pk>/add/relative', views.CriminalAddRelativeView.as_view(),
         name="criminal_add_relative_url"),
    path('registry/criminal/<int:pk>/add/contact-detail', views.CriminalContactDetailAddView.as_view(),
         name="contact-detail_add_url"),
    path('registry/criminal/<int:pk>/add/person', views.CriminalAddContactPersonView.as_view(),
         name="contact_person_add_url"),
    path('registry/criminal/<int:pk>/add/address', views.CriminalAddAddressView.as_view(),
         name="address_add_url"),
    path('registry/criminal/<int:pk>/add/conviction', views.CriminalConvictionAddView.as_view(),
         name="conviction_add_url"),
    path('registry/criminal/<int:pk>/add/criminal-case', views.CriminalCriminalCaseAddView.as_view(),
         name="criminal_case_add_url"),
    path('registry/criminal/<int:pk>/add/manhunt', views.CriminalManhuntAddView.as_view(),
         name="manhunt_add_url"),

    path('registry/criminal/<int:pk>/update/confident', views.CriminalConfidentChangeView.as_view(),
         name="criminal_confident_change_url"),
    path('registry/criminal/<int:pk>/update/owner', views.CriminalOwnerChangeView.as_view(),
         name="criminal_change_owner_url"),
    path('registry/criminal/<int:pk>/update/check', views.criminal_check, name="criminal_check_url"),
    path('registry/criminal/<int:pk>/update/close', views.criminal_close_change, name="criminal_close_change_url"),


    path('registry/cc/', views.cc_list, name="cc_list_url"),
    path('registry/cc/<int:pk>', views.cc_detail, name="cc_detail_url"),

    path('registry/manhunt/', views.manhunt_list, name="manhunt_list_url"),
    path('registry/manhunt/<int:pk>', views.manhunt_detail, name="manhunt_detail_url"),
    path('registry/manhunt/<int:pk>/update', views.ManhuntUpdateView.as_view(), name="manhunt_update_url"),
    path('registry/manhunt/<int:pk>/delete', views.ManhuntDeleteView.as_view(), name="manhunt_delete_url")


]
