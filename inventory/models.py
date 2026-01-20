from django.db import models

# Category class to organize products
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True) # Name of the category. 
    description = models.TextField(blank=True) # The fields can be empty, it is okay.
    is_active = models.BooleanField(default=True) # New categories can be active by default
    slug = models.SlugField(max_length=100, unique=True, blank=True) # Slug field = A URL version of a str
    # A method for displaying the object on admin panel
    def __str__(self):
        return self.name

    class Meta: # Additional settings for the model
        verbose_name = 'Category' # Human-readable name in admin
        verbose_name_plural = 'Categories' # Plural name in admin
        ordering = ['name'] # Sort categories by name
    

    
    def save(self, *args, **kwargs):
        from django.utils.text import slugify
        # If slug is empty, create it from the name
        if not hasattr(self, 'slug') or not self.slug:
            self.slug = slugify(self.name)
         
        # Call the original save()
        super().save(*args, **kwargs)

class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True,verbose_name='SKU Code') # sku - Unique indentifier for the product
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    current_stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True) # True or False
    created_at = models.DateTimeField(auto_now_add=True) # Set on creation
    updated_at = models.DateTimeField(auto_now=True) # Update on every save

    def __str__(self):
        return f'{self.name} ({self.sku})'
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = "Products"
        ordering = ['name'] # Sort by name

    def profit_margin(self):
        if self.cost_price > 0:
            margin = ((self.selling_price - self.cost_price) / self.cost_price) * 100
            return round(margin, 2) # Round to 2 decimal Places
        return 0
    
    def profit_per_unit(self):
        return self.selling_price - self.cost_price
    
    def total_stock_value(self):
        return self.current_stock * self.cost_price
    
    def is_low_stock(self, threshold=10):
        return self.current_stock < threshold
    
    def get_stock_movements(self):
        return self.stock_movement_set.all()

class StockMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=50)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product.name} - {self.movement_type}'
    
