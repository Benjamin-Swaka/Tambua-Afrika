from django import forms
from .models import FAQ, FAQCategory


class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ["category", "question", "answer", "order", "is_active"]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "question": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. How do I reset my password?",
            }),
            "answer": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Write a clear, concise answer...",
            }),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class FAQCategoryForm(forms.ModelForm):
    class Meta:
        model = FAQCategory
        fields = ["name", "order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Category name"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }
