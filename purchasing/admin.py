from django.contrib import admin
from .models import Supplier, PurchaseOrder, PurchaseOrderItem

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Admin for Suppliers"""
    
    list_display = ('name', 'contact_person', 'email', 'phone', 'rating', 'is_active')
    search_fields = ('name', 'email', 'phone', 'contact_person')
    list_filter = ('is_active', 'rating')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'contact_person')
        }),
        ('Contact Details', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Business Information', {
            'fields': ('tax_id', 'payment_terms', 'lead_time_days')
        }),
        ('Rating & Notes', {
            'fields': ('rating', 'notes')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    fields = ('product', 'quantity', 'unit_cost', 'subtotal')
    readonly_fields = ('subtotal',)

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    """Admin for Purchase Orders"""
    
    list_display = ('order_number', 'supplier', 'order_date', 'status', 'total_amount')
    search_fields = ('order_number', 'supplier__name')
    list_filter = ('status', 'order_date')
    
    readonly_fields = ('order_number', 'subtotal', 'total_amount', 'created_at', 'updated_at','created_by', 'order_date')
    
    inlines = [PurchaseOrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'supplier', 'order_date', 'expected_delivery', 'status')
        }),
        ('Financial', {
            'fields': ('subtotal', 'tax_amount', 'shipping_cost', 'total_amount')
        }),
        ('Additional', {
            'fields': ('notes',)
        }),
    )
