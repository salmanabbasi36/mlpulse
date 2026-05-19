from django import forms
from .models import Comment, Newsletter


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your name', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'your@email.com', 'class': 'form-control'}),
            'body': forms.Textarea(attrs={'placeholder': 'Share your thoughts...', 'rows': 4, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False
        self.fields['email'].required = False


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com', 'class': 'newsletter-input'}),
        }
