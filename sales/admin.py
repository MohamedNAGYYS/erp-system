from django.contrib import admin
from .models import Customer
from .models import SalesOrderItem, SalesOrder

# Register your models here.

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'contact_person',
        'email',
        'phone',
        'credit_limit',
        'current_balance',
        'is_active'
    )

    # Search box
    search_fields = ('name', 'email', 'phone', 'contact_person')

    # Filter in sidebar
    list_filter = ('is_business', 'is_active')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'contact_person', 'is_business')
        }),

        ("Contact Details", {
            'fields': ('email', 'phone', 'address')
        }),

        ('Business Details', {
            'fields': ('tax_id',)
        }),
        ('Credit Management', {

            'fields':('credit_limit', 'current_balance')
        }),
        ('Status', {

            'fields': ('is_active',)
        }),

    )
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20




class SalesOrderItemInline(admin.TabularInline):
    model = SalesOrderItem
    extra = 1
    fields = ('product', 'quantity', 'unit_price', 'subtotal')
    readonly_fields = ('subtotal', )

@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'customer',
        'order_date',
        'status',
        'total_amount'
    )

    search_fields = ('order_number', 'customer__name')
    
    # Filters
    list_filter = ('status', 'order_date')


    readonly_fields = (
        'order_number',
        'subtotal',
        'total_amount',
        'created_at',
        'updated_at'
    )

    inlines = [SalesOrderItemInline]


    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'order_date', 'status')
        }),
        ('Financial', {
            'fields': ('subtotal', 'tax_amount', 'total_amount')
        }),
        ('Additional', {
            'fields': ('notes', 'created_by')
        }),
    )