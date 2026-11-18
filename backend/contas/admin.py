from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    ordering = ["email"]
    list_display = ["email", "tipo", "is_active", "is_staff", "criado_em"]
    list_filter = ["tipo", "is_active", "is_staff"]
    search_fields = ["email"]
    readonly_fields = ["uuid", "last_login", "criado_em"]
    show_full_result_count = False
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Perfil", {"fields": ["tipo", "uuid"]}),
        ("Permissões", {"fields": ["is_active", "is_staff", "is_superuser", "groups", "user_permissions"]}),
        ("Datas", {"fields": ["last_login", "criado_em"]}),
    ]
    add_fieldsets = [
        (None, {"classes": ["wide"], "fields": ["email", "tipo", "password1", "password2"]}),
    ]