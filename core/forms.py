from django import forms
from .models import NewsletterSubscriber
from django import forms
from django.forms import inlineformset_factory
from .models import Campaign, Reward, Pledge

class NewsletterForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control rounded-0 border-0',
        'placeholder': 'Enter your email address',
        'aria-label': 'Email address'
    }))

    class Meta:
        model = NewsletterSubscriber
        fields = ['email']



class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ["title", "description", "goal_amount", "deadline", "department"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6, "class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "goal_amount": forms.NumberInput(attrs={"class": "form-control", "min": "1", "step": "0.01"}),
            "deadline": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "department": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensures the datetime-local widget pre-fills correctly on edit
        self.fields["deadline"].input_formats = ["%Y-%m-%dT%H:%M"]


RewardFormSet = inlineformset_factory(
    Campaign,
    Reward,
    fields=["title", "description", "amount"],
    extra=1,
    can_delete=True,
    widgets={
        "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Reward title"}),
        "description": forms.Textarea(
            attrs={"class": "form-control", "rows": 2, "placeholder": "What backers get"}
        ),
        "amount": forms.NumberInput(attrs={"class": "form-control", "min": "1", "step": "0.01"}),
    },
)


class PledgeForm(forms.ModelForm):
    class Meta:
        model = Pledge
        fields = ["reward", "amount"]
        widgets = {
            "reward": forms.Select(attrs={"class": "form-select", "id": "id_reward"}),
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "step": "0.01", "id": "id_amount"}
            ),
        }

    def __init__(self, *args, campaign=None, **kwargs):
        super().__init__(*args, **kwargs)
        if campaign is not None:
            self.fields["reward"].queryset = campaign.rewards.all()
        self.fields["reward"].required = False

    def clean(self):
        cleaned_data = super().clean()
        reward = cleaned_data.get("reward")
        amount = cleaned_data.get("amount")

        if reward and not amount:
            # JS normally fills this in, but guard server-side too
            cleaned_data["amount"] = reward.amount
        elif not reward and not amount:
            raise forms.ValidationError("Enter a pledge amount or select a reward tier.")
        elif reward and amount and amount < reward.amount:
            raise forms.ValidationError(
                f"Pledges selecting '{reward.title}' must be at least {reward.amount}."
            )
        return cleaned_data
