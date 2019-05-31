from django.contrib import admin
from .models import Profile, TrustLevel, Role, Audit, UserLogs

# Register your models here.

admin.site.register(Profile)
admin.site.register(TrustLevel)
admin.site.register(Role)
admin.site.register(Audit)
admin.site.register(UserLogs)
