from django.contrib import admin
from .models import Department, UserProfile, DepartmentMembership, EmailOTP

admin.site.register(Department)
admin.site.register(UserProfile)
admin.site.register(DepartmentMembership)
admin.site.register(EmailOTP)