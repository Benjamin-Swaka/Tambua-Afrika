from django import forms
from django.contrib.auth.models import User
from .models import Submission

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['title', 'category', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title of Work'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }


class AdminSubmissionForm(forms.ModelForm):
    """
    Used only by the custom admin dashboard so staff can create a
    submission on a user's behalf -- e.g. logging a physical/emailed
    entry -- including its poster/cover image. The public-facing
    SubmissionForm above is untouched.
    """
    class Meta:
        model = Submission
        fields = ['user', 'title', 'category', 'file', 'image', 'status']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control rounded-0'}),
            'title': forms.TextInput(attrs={'class': 'form-control rounded-0', 'placeholder': 'Title of Work'}),
            'category': forms.Select(attrs={'class': 'form-control rounded-0'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control rounded-0'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control rounded-0'}),
            'status': forms.Select(attrs={'class': 'form-control rounded-0'}),
        }

    def __init__(self, *args, allowed_categories=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.order_by('username')
        # A department admin can only file submissions into the category(ies)
        # their department owns -- mirrors the same restriction already
        # applied to the moderation queue in admin_submissions().
        if allowed_categories is not None:
            self.fields['category'].choices = [
                (value, label) for value, label in Submission.CATEGORY_CHOICES
                if value in allowed_categories
            ]