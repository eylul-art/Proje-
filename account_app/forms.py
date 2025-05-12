from django import forms
from .models import UserProfile

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'is_private', ]
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Kendini tanıt...',
                'style': 'background-color: rgba(255,255,255,0.8); border-radius: 8px;'
            }),
            'profile_picture': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }
