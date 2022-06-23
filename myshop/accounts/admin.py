from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'number', 'is_published', 'category', 'creator',)
    list_display_links = ('id', 'title')
    search_fields = ('title',)
    list_editable = ('is_published', 'category', 'creator',)
    list_filter = ('is_published', 'creator')
    prepopulated_fields = {"slug": ("title",)}
    exclude = ('views',)
    # readonly_fields = ('creator',)
    list_per_page = 20


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_seller', 'first_name', 'last_name', 'is_active', 'balance')
    list_display_links = ('id', 'username')
    search_fields = ('username',)
    list_editable = ('is_seller',)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('name_seller', 'product', 'price', 'number', 'paid', 'order_number')


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Order, OrderAdmin)