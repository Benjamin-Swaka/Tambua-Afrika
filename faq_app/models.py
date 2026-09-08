from django.db import models
from django.utils.text import slugify


class FAQCategory(models.Model):
    """Optional grouping for FAQs (e.g. 'Billing', 'Getting Started')."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")

    class Meta:
        verbose_name = "FAQ Category"
        verbose_name_plural = "FAQ Categories"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class FAQ(models.Model):
    """A single Frequently Asked Question entry, manageable from admin or the front-end form."""
    category = models.ForeignKey(
        FAQCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faqs",
    )
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first within a category.")
    is_active = models.BooleanField(default=True, help_text="Untick to hide this FAQ without deleting it.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ["category__order", "order", "-created_at"]

    def __str__(self):
        return self.question
