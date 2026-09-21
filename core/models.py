from django.db import models
import random
import string
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.db import models
from django.urls import reverse, NoReverseMatch


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    consent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"
        ordering = ['-created_at']


class Department(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    color = models.CharField(max_length=7, default='#0d0d0d')
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='core_profile'
    )
    primary_department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    onboarding_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email


class DepartmentMembership(models.Model):
    ROLES = [
        ('viewer', 'Viewer'),
        ('contributor', 'Contributor'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES, default='viewer')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'department')

    def __str__(self):
        return f"{self.user.email} - {self.department.name} ({self.role})"


class ConsentLog(models.Model):
    """
    GDPR audit trail: a durable, timestamped record of what a person
    consented to and when. The `cookie_consent` cookie is the *live*
    preference the site reads on each request, but cookies can be
    cleared or expire -- this table is the evidence we can point to if
    a data-protection question ever comes up ("what did this person
    agree to, and when?").
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='consent_logs',
        help_text="Null for anonymous/pre-login consent.",
    )
    session_key = models.CharField(max_length=40, blank=True)
    essential = models.BooleanField(default=True)
    analytics = models.BooleanField(default=False)
    marketing = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        who = self.user.email if self.user else f"session:{self.session_key[:8]}"
        return f"{who} @ {self.created_at:%Y-%m-%d %H:%M}"


class FeaturedWork(models.Model):
    """A single item in the homepage 'Featured Works' carousel."""
    CATEGORY_CHOICES = [
        ('book', 'Book'),
        ('comic', 'Comic'),
        ('play', 'Play'),
        ('animation', 'Animation'),
    ]

    title = models.CharField(max_length=200)
    department_label = models.CharField(
        max_length=100,
        help_text="Shown as the small eyebrow label, e.g. 'Tambua Ink'.",
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='book')
    author_meta = models.CharField(
        max_length=150,
        help_text="e.g. 'by A. K. Mwangi · 2025'",
        blank=True,
    )
    link_url = models.CharField(
        max_length=300, blank=True,
        help_text="Where the 'Read More' / 'Explore' button goes. Leave blank for '#'.",
    )
    link_text = models.CharField(max_length=40, default='Read More')
    background_color = models.CharField(max_length=7, default='#e8e0d8')
    icon_emoji = models.CharField(max_length=8, default='📖')
    image = models.ImageField(upload_to='home/featured_works/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class HomeDepartment(models.Model):
    ACCENT_CHOICES = [
        ('studios', 'Studios (Black)'),
        ('ink',     'Tambua Ink (Royal Blue)'),
        ('stage',   'Tambua Stage (Chocolate Brown)'),
        ('comics',  'Tambua Comics (Silver Grey)'),
        ('sales',   'Sales & Marketing (Beige / Gold)'),
    ]

    ICON_CHOICES = [
        ('studios', 'Studio Box'),
        ('ink',     'Ink Pen'),
        ('stage',   'Theatre / People'),
        ('comics',  'Comics Grid'),
        ('sales',   'Commerce Crosshair'),
    ]

    name        = models.CharField(max_length=120, help_text="e.g. Tambua Afrika Ink")
    label       = models.CharField(max_length=50,  help_text="e.g. Publishing, Core, Theatre")
    description = models.TextField(max_length=300, help_text="Max 300 characters.")
    accent      = models.CharField(max_length=20, choices=ACCENT_CHOICES, default='studios')
    icon        = models.CharField(max_length=20, choices=ICON_CHOICES,   default='studios')
    link_url    = models.CharField(
        max_length=200, blank=True,
        help_text="Named URL (e.g. 'ink_home') or full URL (https://…)."
    )
    link_text   = models.CharField(max_length=50, default="Learn More")
    order       = models.PositiveIntegerField(default=0)
    is_active   = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Home Department"
        verbose_name_plural = "Home Departments"

    def __str__(self):
        return self.name

    def get_link(self):
        """Resolve a named URL or pass through a full/absolute path."""
        if not self.link_url:
            return '#'
        if self.link_url.startswith(('http://', 'https://', '/')):
            return self.link_url
        try:
            return reverse(self.link_url)
        except NoReverseMatch:
            return '#'

class OpenCall(models.Model):
    """A single item in the homepage 'Open Calls' section."""
    STATUS_OPEN = 'open'
    STATUS_CLOSING_SOON = 'closing_soon'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_CLOSING_SOON, 'Closing Soon'),
        (STATUS_CLOSED, 'Closed'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        help_text="Used in the open call's own URL. Auto-generated from the title if left blank.",
    )
    description = models.TextField(help_text="Short summary shown on the open call card.")
    guidelines = models.TextField(
        blank=True,
        help_text=(
            "Full submission guidelines shown on this call's own dedicated page "
            "(eligibility, format, judging criteria, etc). Leave blank to just "
            "show the short summary above on that page too."
        ),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    deadline_label = models.CharField(
        max_length=100,
        help_text="e.g. 'Closes 31 Dec 2026' — free text so past calls can say 'Closed 30 Jun 2026'.",
    )
    categories_label = models.CharField(
        max_length=200,
        help_text="e.g. 'Manuscripts · Poetry · Short Stories · Scripts'",
    )
    link_url = models.CharField(
        max_length=300, blank=True,
        help_text=(
            "Optional external URL (e.g. guidelines hosted elsewhere). When set, "
            "'View Guidelines' sends people straight there instead of to this "
            "call's own details page. Leave blank to use the details page."
        ),
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'open-call'
            slug = base_slug
            counter = 2
            while OpenCall.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('open_call_detail', kwargs={'slug': self.slug})


class ShopHighlight(models.Model):
    """A single item in the homepage 'Shop Highlights' carousel."""
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=250)
    price_label = models.CharField(max_length=60, help_text="e.g. 'From $14.99'")
    link_url = models.CharField(
        max_length=300, blank=True,
        help_text="Leave blank to use the Shop homepage.",
    )
    link_text = models.CharField(max_length=40, default='Browse')
    background_color = models.CharField(max_length=7, default='#e8e0d8')
    icon_emoji = models.CharField(max_length=8, default='🛍️')
    image = models.ImageField(upload_to='home/shop_highlights/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class EmailOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()

    @classmethod
    def generate_otp(cls, user):
        code = ''.join(random.choices(string.digits, k=6))
        return cls.objects.create(user=user, code=code)
    




class Campaign(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_LIVE = "live"
    STATUS_FUNDED = "funded"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_LIVE, "Live"),
        (STATUS_FUNDED, "Funded"),
        (STATUS_FAILED, "Failed"),
    ]

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="crowdfunding_campaigns",
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220, blank=True)
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    raised_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deadline = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)

    # String reference avoids a direct import of Department, which
    # sidesteps circular-import issues if Department itself ever
    # imports from a module that imports Campaign.
    department = models.ForeignKey(
        "core.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="crowdfunding_campaigns",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            # Ensure uniqueness without relying on DB-level retry loops
            while Campaign.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("campaign_detail", kwargs={"slug": self.slug})

    @property
    def progress_percent(self):
        if not self.goal_amount:
            return 0
        pct = (self.raised_amount / self.goal_amount) * 100
        return min(round(float(pct), 1), 100)

    @property
    def days_remaining(self):
        delta = self.deadline - timezone.now()
        return max(delta.days, 0)

    @property
    def is_active(self):
        return self.status == self.STATUS_LIVE and self.deadline > timezone.now()


class Reward(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="rewards")
    title = models.CharField(max_length=150)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["amount"]

    def __str__(self):
        return f"{self.title} ({self.campaign.title})"


class Pledge(models.Model):
    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="crowdfunding_pledges",
    )
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="pledges")
    reward = models.ForeignKey(
        Reward, on_delete=models.SET_NULL, null=True, blank=True, related_name="pledges"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} -> {self.campaign} ({self.amount})"



class ContactMessage(models.Model):
    """Stores messages submitted through the public contact form."""

    SUBJECT_GENERAL = 'general'
    SUBJECT_INK = 'ink'
    SUBJECT_STAGE = 'stage'
    SUBJECT_SHOP = 'shop'

    SUBJECT_CHOICES = [
        (SUBJECT_GENERAL, 'General Inquiry'),
        (SUBJECT_INK, 'Tambua Ink'),
        (SUBJECT_STAGE, 'Tambua Stage'),
        (SUBJECT_SHOP, 'Shop Support'),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default=SUBJECT_GENERAL)
    message = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    # Lightweight metadata for moderation/security auditing — never shown publicly
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.name} — {self.get_subject_display()} ({self.created_at:%Y-%m-%d %H:%M})"
