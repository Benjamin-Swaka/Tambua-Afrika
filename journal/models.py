from django.db import models
from django.contrib.auth.models import User

class Article(models.Model):
    TAGS = (('ink', 'Ink'), ('stage', 'Stage'), ('comics', 'Comics'), ('news', 'Corporate'))
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tag = models.CharField(max_length=20, choices=TAGS)
    image = models.ImageField(upload_to='journal/')
    content = models.TextField() # In production, use a RichTextEditor like CKEditor
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title