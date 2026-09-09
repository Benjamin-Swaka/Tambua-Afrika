from django import forms
from .models import Intent


class IntentForm(forms.ModelForm):
    class Meta:
        model = Intent
        fields = ["name", "trigger_phrases", "response", "priority", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Opening hours",
            }),
            "trigger_phrases": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "One phrase per line, e.g.\nopening hours\nwhat time are you open\nwhen open",
            }),
            "response": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "The reply visitors will see.",
            }),
            "priority": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
                "role": "switch",
            }),
        }
        help_texts = {
            "trigger_phrases": "One phrase or keyword per line. Matches if a visitor's message contains any of these (not case sensitive).",
            "priority": "Higher numbers are checked first when several intents could match the same message.",
        }
