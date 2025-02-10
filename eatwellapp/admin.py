from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Customer, StoreOwner, Restaurant, Food, Order, OrderItem

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'phone_number', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_type', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone_number', 'password1', 'password2', 'user_type'),
        }),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'residential_address', 'location')
    list_filter = ('location',)
    search_fields = ('user__username', 'user__email', 'residential_address')

class StoreOwnerAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_name', 'business_location', 'business_address')
    list_filter = ('business_location',)
    search_fields = ('user__username', 'user__email', 'business_name')

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'location')
    list_filter = ('location',)
    search_fields = ('name', 'owner__business_name')

class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'price')
    list_filter = ('restaurant',)
    search_fields = ('name', 'restaurant__name')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'address', 'restaurant', 'created_at', 'total_amount', 'is_paid')
    list_filter = ('is_paid', 'payment_method', 'created_at')
    search_fields = ('customer__user__username', 'restaurant__name')
    inlines = [OrderItemInline]

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(StoreOwner, StoreOwnerAdmin)
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Food, FoodAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)

