from django import forms
from django.forms import ModelForm

from press.models import Post, Category, POST_LABELED_STATUS


class PostCustomForm(forms.Form):
    title = forms.TextInput(attrs={'class': 'form-control'})
    body = forms.Textarea(attrs={'class': 'form-control'})
    image_link = forms.TextInput(attrs={'class': 'form-control'})
    category = forms.Select(attrs={'class': 'form-control'},
                            choices=Category.objects.values_list('id', 'label'))
    status = forms.Select(attrs={'class': 'form-control'}, choices=POST_LABELED_STATUS)

    def save(self):
        data = self.cleaned_data()
        post = Post.objects.create(**data)
        post.save()


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
