from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Adiciona o campo 'tipo' ao list_display, fieldsets e add_fieldsets
    list_display = ('username', 'email', 'first_name', 'last_name', 'tipo', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('tipo', 'profile_picture_url')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {'fields': ('tipo', 'profile_picture_url')}),
    )
