import re

from django import forms
from .models import NewsletterSubscriber, FeaturedWork, OpenCall, ShopHighlight
from django import forms
from django.forms import inlineformset_factory
from .models import Campaign, Reward, Pledge
from django.core.validators import validate_email
from .models import ContactMessage
NAME_RE = re.compile(r"^[A-Za-z\u00C0-\u024F' \-]+$")
URL_RE = re.compile(r'https?://|www\.', re.IGNORECASE)


class NewsletterForm(forms.ModelForm):
    consent = forms.BooleanField(
        required=True,
        label='I agree to receive email updates',
        widget=forms.CheckboxInput(attrs={
            'id': 'footer-consent',
        })
    )

    class Meta:
        model = NewsletterSubscriber
        fields = ['email']  # consent is handled separately
        widgets = {
            'email': forms.EmailInput(attrs={
                'id': 'footer-email',
                'class': 'ta-footer-input',
                'placeholder': 'your@email.com',
                'autocomplete': 'email',
                'required': True,
            }),
        }

class FeaturedWorkForm(forms.ModelForm):
    class Meta:
        model = FeaturedWork
        fields = [
            'title', 'department_label', 'category', 'author_meta',
            'link_url', 'link_text', 'background_color', 'icon_emoji',
            'image', 'is_active', 'order',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'department_label': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'category': forms.Select(attrs={'class': 'form-select rounded-0'}),
            'author_meta': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'link_url': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'link_text': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'background_color': forms.TextInput(attrs={'class': 'form-control rounded-0', 'type': 'color'}),
            'icon_emoji': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control rounded-0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control rounded-0'}),
        }


class OpenCallForm(forms.ModelForm):
    class Meta:
        model = OpenCall
        fields = [
            'title', 'slug', 'description', 'guidelines', 'status', 'deadline_label',
            'categories_label', 'link_url', 'is_active', 'order',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'slug': forms.TextInput(attrs={'class': 'form-control rounded-0', 'placeholder': 'auto-generated-if-blank'}),
            'description': forms.Textarea(attrs={'class': 'form-control rounded-0', 'rows': 3}),
            'guidelines': forms.Textarea(attrs={'class': 'form-control rounded-0', 'rows': 8}),
            'status': forms.Select(attrs={'class': 'form-select rounded-0'}),
            'deadline_label': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'categories_label': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'link_url': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control rounded-0'}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug', '').strip()
        return slug  # blank is fine -- OpenCall.save() auto-generates it


class ShopHighlightForm(forms.ModelForm):
    class Meta:
        model = ShopHighlight
        fields = [
            'title', 'description', 'price_label', 'link_url', 'link_text',
            'background_color', 'icon_emoji', 'image', 'is_active', 'order',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'description': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'price_label': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'link_url': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'link_text': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'background_color': forms.TextInput(attrs={'class': 'form-control rounded-0', 'type': 'color'}),
            'icon_emoji': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control rounded-0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control rounded-0'}),
        }




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




class ContactForm(forms.ModelForm):
    """
    Public-facing contact form.

    Every field is validated server-side with our own friendly messages
    (rather than Django's generic "This field is required."), and every
    invalid field gets Bootstrap's red 'is-invalid' outline automatically.

    Also includes a hidden honeypot field ('website') to catch simple bots.
    """

    name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control tmb-input',
            'placeholder': 'Your Name',
            'autocomplete': 'name',
        })
    )
    email = forms.CharField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control tmb-input',
            'placeholder': 'Your Email',
            'autocomplete': 'email',
        })
    )
    subject = forms.ChoiceField(
        required=False,
        choices=[('', 'Subject / Department')] + ContactMessage.SUBJECT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select tmb-input'}),
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control tmb-input',
            'placeholder': 'Your Message',
            'rows': 5,
        })
    )

    # Honeypot: real visitors never see or fill this. Any bot that fills
    # every field on a page will usually fill this too, so we quietly
    # reject the submission when it's non-empty.
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'tabindex': '-1', 'autocomplete': 'off'})
    )

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Outline every invalid field in red, so errors are obvious
        # without needing extra logic in the template.
        if self.is_bound:
            for name in self.errors:
                if name in self.fields:
                    widget = self.fields[name].widget
                    widget.attrs['class'] = (widget.attrs.get('class', '') + ' is-invalid').strip()

    def clean_website(self):
        value = self.cleaned_data.get('website')
        if value:
            raise forms.ValidationError('Submission could not be processed.')
        return value

    def clean_name(self):
        name = (self.cleaned_data.get('name') or '').strip()
        if not name:
            raise forms.ValidationError('Please tell us your name.')
        if len(name) < 2:
            raise forms.ValidationError('Please enter your full name.')
        if not NAME_RE.match(name):
            raise forms.ValidationError('Name can only contain letters, spaces and hyphens.')
        return name

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        if not email:
            raise forms.ValidationError('Please enter your email address.')
        try:
            validate_email(email)
        except forms.ValidationError:
            raise forms.ValidationError('Please enter a valid email address.')
        return email

    def clean_subject(self):
        subject = self.cleaned_data.get('subject') or ''
        if not subject:
            raise forms.ValidationError('Please choose a subject / department.')
        return subject

    def clean_message(self):
        message = (self.cleaned_data.get('message') or '').strip()
        if not message:
            raise forms.ValidationError('Please enter a message.')
        if len(message) < 10:
            raise forms.ValidationError('Please enter a more detailed message (at least 10 characters).')
        if len(URL_RE.findall(message)) > 1:
            raise forms.ValidationError('Please remove extra links from your message.')
        return message