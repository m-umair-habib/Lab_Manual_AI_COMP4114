from django import forms
from .models import Dynamic_QR

class QRCodeForm(forms.ModelForm):
    class Meta:
        model = Dynamic_QR
        fields = ['redirect_url']  # user inputs only the URL
        widgets = {
            'redirect_url': forms.URLInput(attrs={'placeholder': 'Enter URL here'})
        }

class UpdateQRForm(forms.ModelForm):
    class Meta:
        model = Dynamic_QR
        fields = ['redirect_url']  # Only allow changing the URL
        widgets = {
            'redirect_url': forms.URLInput(attrs={'placeholder': 'Enter new URL'})
        }