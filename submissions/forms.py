from django import forms
from django_summernote.widgets import SummernoteWidget
from .models import Submission


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['author_name', 'author_email', 'author_bio', 'title', 'excerpt', 'body', 'category', 'tags', 'cover_image']
        widgets = {
            'body': SummernoteWidget(),
            'author_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name'}),
            'author_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'}),
            'author_bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief bio (shown with your article)'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Article title'}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'A short summary (shown in listings)'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'python, neural-networks, llm'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
