"""
SIGNALS for Purchasing app
Automatically update inventory when purchase orders are received
"""

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import PurchaseOrder
from inventory.models import Product

@receiver(pre_save, sender=PurchaseOrder)
def update_inventory_on_purchase_received(sender, instance, **kwargs):
    if not instance.pk:
        return
    
    try:
        # Get old order from database
        old_order = PurchaseOrder.objects.get(pk=instance.pk)
        old_status = old_order.status
        new_status = instance.status
    except PurchaseOrder.DoesNotExist:
        return
    
    # Only process if status changed
    if old_status != new_status:
        print(f"Purchase Order {instance.order_number} changed from {old_status} to {new_status}")
        
        items = instance.items.all()
        
        
        if new_status == 'received' and old_status != 'received':
            print(f"  -> Increasing stock for {items.count()} items")
            
            for item in items:
                product = item.product
                old_stock = product.current_stock
                
                product.current_stock += item.quantity
                
                # Formula: New average = (old_total_value + new_total_value) / total_quantity
                old_total_value = product.cost_price * old_stock
                new_total_value = item.unit_cost * item.quantity
                total_quantity = old_stock + item.quantity
                
                if total_quantity > 0:
                    product.cost_price = (old_total_value + new_total_value) / total_quantity
                
            
                product.save()
                
                print(f"    + {product.name}: {old_stock} -> {product.current_stock}")
                print(f"      Cost: ${product.cost_price:.2f} (was ${old_total_value/old_stock if old_stock>0 else 0:.2f})")
                
                try:
                    from inventory.models import StockMovement
                    StockMovement.objects.create(
                        product=product,
                        movement_type='purchase',
                        quantity=item.quantity,
                        reference=instance.order_number,
                        notes=f"Purchase Order {instance.order_number}"
                    )
                except:
                    pass  # Skip if StockMovement doesn't exist yet
        
        elif old_status == 'received' and new_status == 'cancelled':
            print(f"  -> Decreasing stock (cancelling received order)")
            
            for item in items:
                product = item.product
                old_stock = product.current_stock
                
                # Check if we have enough stock to remove
                if product.current_stock >= item.quantity:
                    product.current_stock -= item.quantity
                    product.save()
                    
                    print(f"    - {product.name}: {old_stock} -> {product.current_stock}")
                    
                    # Create stock movement
                    try:
                        from inventory.models import StockMovement
                        StockMovement.objects.create(
                            product=product,
                            movement_type='return_to_supplier',
                            quantity=-item.quantity,
                            reference=instance.order_number,
                            notes=f"Cancelled PO: {instance.order_number}"
                        )
                    except:
                        pass

@receiver(post_save, sender=PurchaseOrder)
def update_purchase_order_totals(sender, instance, created, **kwargs):
    """Update totals after saving"""
    if created or instance.status == 'draft':
        instance.calculate_totals()