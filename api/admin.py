from django.contrib import admin
from .models import Category, Product, Message, AdminUser


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "label", "icon_key", "created_at")
    search_fields = ("id", "label")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "badge", "rating", "created_at")
    list_filter = ("badge", "category")
    search_fields = ("name",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "is_read", "is_pinned", "is_archived", "created_at")
    list_filter = ("is_read", "is_pinned", "is_archived")
    search_fields = ("name", "email")


@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "last_login", "created_at")
    search_fields = ("email",)
    exclude = ("password_hash", "otp_code")  # ne pas afficher les champs sensibles
