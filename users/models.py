from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    ROLES = (
        ('creator', 'Creator/Reader'),
        ('staff', 'Staff/Admin'),
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='users_profile'   # unique reverse name
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/default.png',
        blank=True
    )
    bio = models.TextField(max_length=500, blank=True)
    role = models.CharField(max_length=20, choices=ROLES, default='creator')
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'{self.user.email} Profile'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile whenever a new User is created."""
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the profile whenever the user is saved (if it exists)."""
    if hasattr(instance, 'users_profile'):
        instance.users_profile.save()