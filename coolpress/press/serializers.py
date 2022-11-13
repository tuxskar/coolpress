from django.contrib.auth.models import User
from rest_framework import serializers

from press.models import Post, Category, CoolUser


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'category', 'author', 'creation_date']
        read_only_fields = ('author',)
        ordering = ['-creation_date']


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class AuthorSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(
        many=False,
        read_only=True,
    )

    class Meta:
        model = CoolUser
        fields = ['id', 'user', 'github_profile']
