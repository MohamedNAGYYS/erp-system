from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomerUser

class CustomUserAdmin(UserAdmin):
    """Admin interface for Custom User Model"""
    
    # Fields to display in list view
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    
    # Filters for sidebar
    list_filter = ('role', 'is_staff', 'is_active')
    
    # Fields to show in edit form
    fieldsets = UserAdmin.fieldsets + (
        ('ERP Information', {'fields': ('role', 'phone', 'department')}),
    )
    
    # Fields to show in create form
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('ERP Information', {'fields': ('role', 'phone', 'department')}),
    )

# Register the model
admin.site.register(CustomerUser, CustomUserAdmin)