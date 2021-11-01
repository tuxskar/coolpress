from django import forms
from django.forms import ModelForm

from press.models import Post, Category, CoolUser


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


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['slug', 'label']
        widgets = {
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'label': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CoolUserForm(ModelForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    github_profile = forms.CharField(max_length=254,
                                     help_text='Required. Inform a valid email address.')

    class Meta:
        model = CoolUser
        fields = ('github_profile',)
