from django import forms
from .models import UserImage, ShirtImage

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = UserImage
        fields = ['image']