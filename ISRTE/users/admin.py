from django.contrib import admin
from .models import Profile, TrustLevel, Role

# Register your models here.

admin.site.register(Profile)
admin.site.register(TrustLevel)
admin.site.register(Role)