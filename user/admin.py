from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Profile
from .forms import UserRegistrationForm, UserEditForm

User = get_user_model()


class UserAdmin(BaseUserAdmin):
    form = UserEditForm
    add_form = UserRegistrationForm
    list_display = ('email', 'name', 'is_admin')
    list_filter = ('is_admin', 'email',)
    fieldsets = (
        ('Main', {'fields': ('email', 'name', 'password')}),
        ('Permissions', {'fields': ('is_admin', 'is_active',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'name')
    ordering = ('date_joined', 'email')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'verified', 'level')
    list_filter = ('verified', 'level')
    search_fields = ('username',)


admin.site.register(User, UserAdmin)
