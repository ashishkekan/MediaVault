# gallery/forms.py

from django import forms
from .models import MediaFile

class UploadForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ['file']  # Only file field

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = file.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                self.instance.media_type = 'photo'
            elif ext in ['mp4', 'avi', 'mov', 'mkv']:
                self.instance.media_type = 'video'
            elif ext in ['pdf', 'doc', 'docx', 'txt']:
                self.instance.media_type = 'document'
            else:
                self.instance.media_type = 'document'  # Default
        return file
    