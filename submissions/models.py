from django.db import models
from django.contrib.auth.models import User

class Submission(models.Model):
    STATUS_CHOICES = (
        ('received', 'Received'),
        ('review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    
    CATEGORY_CHOICES = (
        ('manuscript', 'Book Manuscript'),
        ('script', 'Play Script'),
        ('comic', 'Comic/Art'),
        ('audition', 'Audition Tape'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    file = models.FileField(upload_to='submissions/')
    image = models.ImageField(
        upload_to='submissions/posters/',
        blank=True,
        null=True,
        help_text='Optional cover/poster image for this submission.',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"