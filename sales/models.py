from django.db import models
from django.core.validators import MinValueValidator, EmailValidator
from decimal import Decimal
# Create your models here.

class Customer(models.Model):
    name = models.CharField(max_length=200, help_text="Company name or person's full name")
    contact_person = models.CharField(max_length=100, blank=True, help_text="Main contact person (for businesses)")
    email = models.EmailField(blank=True, validators= [EmailValidator()], help_text="Primary email address")
    phone = models.CharField(max_length=20, blank=True, help_text="Phone number with country code")
    address = models.TextField(blank=True, help_text="Full postal address")
    tax_id = models.CharField(max_length=50, blank=True, verbose_name="Tax ID/VAT Number", help_text="For invoice generation")
    is_business = models.BooleanField(default=False, verbose_name='Business Customer', help_text="Check if this is a business (not individual)")
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=10000.00, validators=[MinValueValidator(Decimal('0.00'))], help_text="Maximum amount customer can owe")
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Amount currently owed by customer")
    is_active = models.BooleanField(default=True, help_text="Deactivate instead of deleting")
    created_at = models.DateTimeField(auto_now_add=True, editable=False) # Set when created, and can't edit maually
    updated_at = models.DateTimeField(auto_now=True, editable=False)


    def __str__(self):
        if self.is_business:
            return f"{self.name} (Business)"
        return f"{self.name} (Individual)"

    def available_credit(self):
        return self.credit_limit - self.current_balance
    
    def can_purchase(self, amount):
        return (self.is_active and self.available_credit() >= amount)
    
    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = "Customers"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
        ]


class SalesOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),          # Just created, not finalized
        ('confirmed', 'Confirmed'),  # Order is confirmed
        ('processing', 'Processing'), # Being prepared
        ('shipped', 'Shipped'),      # Sent to customer
        ('delivered', 'Delivered'),  # Customer received
        ('cancelled', 'Cancelled')
    ]

    order_number = models.CharField(max_length=20, unique=True, editable=False, verbose_name='Order Number')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True, verbose_name='Order Date')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True, help_text="Special instructions or notes")
    created_by = models.ForeignKey('accounts.CustomerUser', on_delete=models.SET_NULL, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __srt__(self):
        return f"{self.order_number} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            last_order = SalesOrder.objects.order_by('id').last() # Get the last order num
            if last_order:
                try:
                    last_num = int(last_order.order_number.split('-')[1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
                
            else:
                new_num = 1
            
            self.order_number = f"SO-{new_num:03d}"

        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        items = self.items.all()
        self.subtotal = sum(item.subtotal for item in items)
        self.total_amount = self.subtotal + self.tax_amount
        self.save()

    class Meta:
        verbose_name = 'Sales Order'
        verbose_name_plural = 'Sales Orders'
        ordering = ['-order_date']

class SalesOrderItem(models.Model):
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey("inventory.Product", on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, editable=False)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

        self.order.calculate_totals()

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = "Order Items"