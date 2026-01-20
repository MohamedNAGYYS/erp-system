from django.db import models
from django.core.validators import MinValueValidator, EmailValidator
from decimal import Decimal
# Create your models here.

class Supplier(models.Model):
    name = models.CharField(max_length=200, help_text="Official company name")
    contact_person = models.CharField(max_length=100, blank=True, help_text="Your main contact at the supplier")
    email = models.EmailField(blank=True, validators= [EmailValidator()], help_text='Primary contact email')
    phone = models.CharField(blank=True, help_text="Business phone number")
    address = models.TextField(blank=True, help_text="Supplier's business address")
    tax_id = models.CharField(max_length=50, blank=True, verbose_name='Tax ID/VAT Number')
    payment_terms = models.CharField(max_length=20, default='net_30', choices=[
            ('net_7', 'Net 7 Days'),
            ('net_15', 'Net 15 Days'),
            ('net_30', 'Net 30 Days'),  
            ('cod', 'Cash on Delivery'),
            ('prepaid', 'Prepaid'),
    ], help_text="Whem payment is due after delivery")

    lead_time_days = models.IntegerField(default=7, validators=[MinValueValidator(1)], help_text="Average days to deliver after order")
    is_active = models.BooleanField(default=True, help_text="Deactive intead of deleting")
    rating = models.IntegerField(default=3, choices=[
        (1, '1 Star'), 
        (2, '2 Stars'), 
        (3, '3 Stars'), 
        (4, '4 Stars'), 
        (5, '5 Stars')],
        help_text="Your rating of this supplier"
    )
    notes =  models.TextField(blank=True,help_text="Additional notes about this supplier")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    

    def get_rating_stars(self):
        return "★" * self.rating + '☆' * (5 - self.rating)
    
    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ['name']


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),          # Just created
        ('sent', 'Sent to Supplier'), # Emailed/faxed to supplier
        ('confirmed', 'Confirmed'),   # Supplier confirmed
        ('received', 'Received'),     # Goods received
        ('cancelled', 'Cancelled'),   # Order cancelled
    ]
    

    order_number = models.CharField( max_length=20,  unique=True, editable=False, verbose_name="PO Number")
    supplier = models.ForeignKey( Supplier,on_delete=models.PROTECT,related_name='purchase_orders')
    order_date = models.DateField(auto_now_add=True)
    expected_delivery = models.DateField( blank=True, null=True,help_text="When supplier promised delivery")
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='draft')
    subtotal = models.DecimalField( max_digits=12,decimal_places=2,default=0.00)
    tax_amount = models.DecimalField( max_digits=12,decimal_places=2,default=0.00)
    shipping_cost = models.DecimalField( max_digits=10, decimal_places=2, default=0.00)
    
    total_amount = models.DecimalField( max_digits=12, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey('accounts.CustomerUser',on_delete=models.SET_NULL,null=True,editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
    def __str__(self):
        return f"PO-{self.order_number} - {self.supplier.name}"
    
    def save(self, *args, **kwargs):
        
        if not self.order_number:
            last_po = PurchaseOrder.objects.order_by('id').last()
            
            if last_po:
                try:
                    last_num = int(last_po.order_number.split('-')[1])
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1
            
            self.order_number = f"PO-{new_num:03d}"
        
        # Auto-set expected delivery if not set
        if not self.expected_delivery and self.supplier:
            from django.utils import timezone
            from datetime import timedelta
            self.expected_delivery = timezone.now().date() + timedelta(days=self.supplier.lead_time_days)
        
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        
        items = self.items.all()
        self.subtotal = sum(item.subtotal for item in items)
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost
        self.save()
    
    class Meta:
        verbose_name = "Purchase Order"
        verbose_name_plural = "Purchase Orders"
        ordering = ['-order_date']


class PurchaseOrderItem(models.Model):
    order = models.ForeignKey( PurchaseOrder,on_delete=models.CASCADE,related_name='items' )
    
    product = models.ForeignKey('inventory.Product',on_delete=models.PROTECT)    
    quantity = models.IntegerField(default=1,validators=[MinValueValidator(1)] )
    
    unit_cost = models.DecimalField( max_digits=10,decimal_places=2,validators=[MinValueValidator(Decimal('0.01'))])
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2,default=0.00,editable=False )
    

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        """Calculate line total"""
        self.subtotal = self.quantity * self.unit_cost
        super().save(*args, **kwargs)
        
        self.order.calculate_totals()
    
    class Meta:
        verbose_name = "Purchase Order Item"
        verbose_name_plural = "Purchase Order Items"