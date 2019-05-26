from django.contrib import admin
from .models import PersonAccess, GroupAccess, RequestToOpen

# Register your models here.

admin.site.register(PersonAccess)
admin.site.register(GroupAccess)
admin.site.register(RequestToOpen)