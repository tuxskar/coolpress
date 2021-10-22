from django.forms import ModelForm, TextInput, Select, Textarea

from press.models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        exclude = ['author', 'word_cloud_link', 'source_link', 'source_label']
        widgets = {
            'title': TextInput(attrs={'class': 'form-control'}),
            'body': Textarea(attrs={'class': 'form-control'}),
            'image_link': TextInput(attrs={'class': 'form-control'}),
            'category': Select(attrs={'class': 'form-control'}),
            'status': Select(attrs={'class': 'form-control'}),
        }
