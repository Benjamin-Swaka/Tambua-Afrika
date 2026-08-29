from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = (
        ('book', 'Book'),
        ('comic', 'Comic'),
        ('merch', 'Merchandise'),
        ('ticket', 'Event Ticket'),
    )
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='shop/products/')
    description = models.TextField()
    is_digital = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name