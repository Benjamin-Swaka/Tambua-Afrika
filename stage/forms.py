from django import forms
from .models import Show


class ShowForm(forms.ModelForm):
    class Meta:
        model = Show
        fields = ['title', 'slug', 'description', 'venue', 'date', 'time', 'price', 'capacity', 'image', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'slug': forms.TextInput(attrs={'class': 'form-control rounded-0', 'placeholder': 'auto-generated-if-blank'}),
            'description': forms.Textarea(attrs={'class': 'form-control rounded-0', 'rows': 4}),
            'venue': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'date': forms.DateInput(attrs={'class': 'form-control rounded-0', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control rounded-0', 'type': 'time'}),
            'price': forms.NumberInput(attrs={'class': 'form-control rounded-0', 'step': '0.01'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control rounded-0'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control rounded-0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_slug(self):
        from django.utils.text import slugify
        slug = self.cleaned_data.get('slug', '').strip()
        if not slug:
            slug = slugify(self.cleaned_data.get('title', ''))
        return slug
