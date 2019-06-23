from django.contrib import admin
from .models import Criminals, Persons, CriminalAddresses, ContactRelation, ContactType, Contacts, \
    PersonAddresses, Occupation, RelativeRelation, Organizations, CriminalsRelatives, CriminalsContactPersons, \
    CriminalCaseCriminals, Review

# Register your models here.

admin.site.register(Criminals)
admin.site.register(Occupation)
admin.site.register(Organizations)
admin.site.register(Persons)
admin.site.register(CriminalAddresses)
admin.site.register(Contacts)
admin.site.register(ContactType)
admin.site.register(ContactRelation)
admin.site.register(RelativeRelation)
admin.site.register(PersonAddresses)
admin.site.register(CriminalsRelatives)
admin.site.register(CriminalsContactPersons)
admin.site.register(CriminalCaseCriminals)
admin.site.register(Review)
