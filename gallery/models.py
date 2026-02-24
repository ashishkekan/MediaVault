# gallery/models.py

from django.db import models
from django.conf import settings


class MediaFile(models.Model):
    MEDIA_TYPES = (
        ("photo", "Photo"),
        ("video", "Video"),
        ("document", "Document"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to="uploads/%Y/%m/%d/")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default="photo")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
