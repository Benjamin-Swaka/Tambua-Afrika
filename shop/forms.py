from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'image', 'description', 'is_digital']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }