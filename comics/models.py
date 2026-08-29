from django.db import models

class Comic(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=100)
    cover_image = models.ImageField(upload_to='comics/covers/')
    description = models.TextField()
    # Link to read online or preview pages
    sample_pdf = models.FileField(upload_to='comics/samples/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title