# gallery/forms.py

from django import forms
from .models import MediaFile, Album


class UploadForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ["file", "category"]  # Only file field

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
            ext = file.name.split(".")[-1].lower()
            if ext in ["jpg", "jpeg", "png", "gif", "bmp"]:
                self.instance.media_type = "photo"
            elif ext in ["mp4", "avi", "mov", "mkv"]:
                self.instance.media_type = "video"
            elif ext in ["pdf", "doc", "docx", "txt"]:
                self.instance.media_type = "document"
            else:
                self.instance.media_type = "document"  # Default
        return file


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "search-input w-full py-3 px-4 rounded-xl",
                    "placeholder": "Album Name",
                }
            ),
        }
