from django import forms
from django.forms import ModelForm

from press.models import Post


class CommentForm(forms.Form):
    body = forms.CharField(label='Add some comment',
                           widget=forms.Textarea(attrs={'class': 'form-control'}))
    votes = forms.IntegerField(label='Vote the post', min_value=1, max_value=10,
                               widget=forms.NumberInput(attrs={'class': 'form-control'}))


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
