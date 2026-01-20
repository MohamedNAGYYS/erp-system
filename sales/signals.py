"""
SIGNALS FOR Sales app
Auto update inventory when orders change
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import SalesOrder
from inventory.models import Product, StockMovement

@receiver(pre_save, sender=SalesOrder)
def update_inventory_on_status_change(sender, instance, **kwargs):
    if not instance.pk:
        return 
    
    try:

        old_order = SalesOrder.objects.get(pk=instance.pk)
        old_status = old_order.status
        new_status = instance.status

    except SalesOrder.DoesNotExist:
        return
    
    if old_order != new_status:
        print(f"Order {instance.order_number} changed from {old_status} to {new_status}")
        items = instance.items.all()

        if new_status == 'confirmed' and old_status != 'confirmed':
            print(f" -> Reducing stock for {items.count()} items")

            for item in items:
                product = items.product
                old_stock = product.current_stock

                if product.current_stock >= item.quantity:
                    # Reduce stock
                    product.current_stock -= item.quantity
                    product.save()


                    StockMovement.objects.create(
                        product=product,
                        warehouse = product.warehouse if hasattr(product, 'warehouse') else None,
                        movement_type = 'sale',
                        quantity = -item.quantity,
                        reference =instance.order_number,
                        notes = f'Sales Order {instance.order_number}'
                    )
                    print(f"        -{product.name}: {old_stock} -> {product.current_stock}")
                else:
                    print(f"    ERROR: Not enough {product.name} in stock!")
        elif old_status == 'confirmed' and new_status == 'cancelled':
            print(f"    -> Adding back stock for {items.count()} items")

            for item in items:
                product = item.product
                old_stock = product.current_stock

                
                product.current_stock += item.quantity
                product.save()


                StockMovement.objects.create(
                    product = product,
                    warehouse = product.warehouse if hasattr(product, 'warehouse') else None,
                    movement_type = 'return',
                    quantity = item.quantity ,
                    reference = instance.order_number,
                    notes = f'Order cancelled: {instance.order_number}'
                )

                print(f"    + {product.name}: {old_stock} -> {product.current_stock}")

@receiver(post_save, sender=SalesOrder)
def update_order_totals(sender, instance, created, **kwargs):
    if created or instance.status == 'draft':
        instance.calculate_totals()