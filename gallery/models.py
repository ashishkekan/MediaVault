# gallery/models.py (update kar)

from django.db import models
from django.conf import settings
from django.utils import timezone

class MediaFile(models.Model):
    MEDIA_TYPES = (
        ('photo', 'Photo'),
        ('video', 'Video'),
        ('document', 'Document'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default='photo')
    size = models.PositiveIntegerField(default=0)  # Add this: file size in bytes
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.file.name
    
    def save(self, *args, **kwargs):
        if self.file:
            self.size = self.file.size  # Auto set size on save
        super().save(*args, **kwargs)
