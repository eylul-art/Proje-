from django import forms
from .models import UserProfile

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write something about yourself...',
                'style': 'background-color: rgba(255,255,255,0.8); border-radius: 8px;'
            }),
            'profile_picture': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }
