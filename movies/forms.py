from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'acting', 'story', 'cinematography']
        widgets = {
    'text': forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 3,
        'placeholder': 'Yorumunuzu yazın...',
        'style': 'background-color: rgba(255,255,255,0.9); color: black; border-radius: 8px;'
    }),
    
    'acting': forms.NumberInput(attrs={'min': 1, 'max': 5}),
    'story': forms.NumberInput(attrs={'min': 1, 'max': 5}),
    'cinematography': forms.NumberInput(attrs={'min': 1, 'max': 5}),

}

