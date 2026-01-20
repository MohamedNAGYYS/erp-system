from django.apps import AppConfig

class PurchasingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'purchasing'
    verbose_name = "Purchasing Management"
    
    def ready(self):
        """Import signals when app is ready"""
        import purchasing.signals  # Connect our signals