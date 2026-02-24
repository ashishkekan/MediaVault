# gallery/forms.py

from django import forms
from .models import MediaFile, Album


class UploadForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ['file', 'category']  # sirf file field

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = file.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                self.instance.media_type = 'photo'
            elif ext in ['mp4', 'mov', 'avi', 'mkv', 'webm']:
                self.instance.media_type = 'video'
            else:
                self.instance.media_type = 'document'  # pdf, doc, txt, sab document
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
