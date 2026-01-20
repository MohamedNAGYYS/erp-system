from django.contrib import admin
from .models import Category
from .models import Product

@admin.register(Category)

# Custom Admin configuration
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active') # Which fields to show in the list view
    search_fields = ('name', 'description') # I can search in by these fields
    list_filter = ('is_active', ) # Add filter sidebar. Filter options in the sidebar
    prepopulated_fields = {'slug':('name',)} # Auto-fill slug from name


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'current_stock', 'selling_price', 'is_active')
    search_fields = ('name', 'sku', 'description')
    list_filter = ('category', 'is_active')

    # Fields to show in edit form
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'sku', 'description', 'category')
        }),

        ("Pricing", {
            'fields' : ('cost_price', 'selling_price')
        }),
     
        ('Inventory', {
            'fields': ('current_stock', 'is_active')
        }),
    
    )
    