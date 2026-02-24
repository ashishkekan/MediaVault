# gallery/models.py (update kar)

from django.db import models
from django.conf import settings
from django.utils import timezone


class MediaFile(models.Model):
    MEDIA_TYPES = (
        ("photo", "Photo"),
        ("video", "Video"),
        ("document", "Document"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to="uploads/%Y/%m/%d/")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default="photo")
    size = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=50, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Many-to-Many with Album
    albums = models.ManyToManyField("Album", related_name="media_files", blank=True)

    def __str__(self):
        return self.file.name

    class Meta:
        ordering = ["-uploaded_at"]

    def delete(self, *args, **kwargs):  # Override for soft delete
        self.is_deleted = True
        self.save()

    def save(self, *args, **kwargs):
        if self.file:
            self.size = self.file.size  # Auto set size on save
        super().save(*args, **kwargs)


class Album(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    cover = models.ForeignKey(
        MediaFile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="album_covers",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-updated_at"]

    @property
    def media_count(self):
        return self.media_files.count()
