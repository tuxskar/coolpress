from enum import Enum

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class CoolUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    github_profile = models.CharField(max_length=150, null=True, blank=True)
    gh_stars = models.IntegerField(null=True, blank=True)
    gh_repositories = models.IntegerField(null=True, blank=True)
    gravatar_link = models.CharField(max_length=400, null=True, blank=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} ({self.user.username})'


class Category(models.Model):
    class Meta:
        verbose_name_plural = "categories"

    label = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.slug}'


class PostStatus(Enum):
    DRAFT = 'DRAFT'
    PUBLISHED = 'PUBLISHED'


class Post(models.Model):
    STATUS = [
        (PostStatus.DRAFT.value, 'Draft'),
        (PostStatus.PUBLISHED.value, 'Published post'),
    ]

    title = models.CharField(max_length=400)
    body = models.TextField()
    image_link = models.CharField(max_length=400, null=True, blank=True)

    chart_link = models.CharField(max_length=400, null=True, blank=True)
    word_cloud_link = models.CharField(max_length=400, null=True, blank=True)

    source_link = models.CharField(max_length=400, null=True, blank=True)
    source_label = models.CharField(max_length=400, null=True, blank=True)

    status = models.CharField(
        max_length=32,
        choices=STATUS,
        default=PostStatus.DRAFT,
    )

    author = models.ForeignKey(CoolUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} - by {self.author.user.username}'