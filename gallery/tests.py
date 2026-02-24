from django.test import TestCase
from django.contrib.auth.models import User
from .models import MediaFile


class MediaTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="123")

    def test_media_creation(self):
        file = MediaFile.objects.create(user=self.user, file="test.jpg")
        self.assertEqual(file.media_type, "photo")
