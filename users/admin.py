from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserPasswordHistory, Profile, Setting, CustomPermission


@admin.register(User)
class MyUserAdmin(UserAdmin):
    fieldsets = (
        ('Account information', {'fields': ('username', 'password')}),
        (_('Personal info'), {
         'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'permissions', 'user_permissions', 'groups'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )


admin.site.register(Profile)
admin.site.register(Setting)
admin.site.register(CustomPermission)
admin.site.register(UserPasswordHistory)