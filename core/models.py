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

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email


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
