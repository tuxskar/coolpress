from django import forms
from django.forms import ModelForm

from press.models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body', 'image_link', 'category', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control'}),
            'image_link': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }