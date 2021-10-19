from enum import Enum

from django.contrib.auth.models import User
from django.db import models


class CoolUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    github_profile = models.CharField(max_length=150, null=True, blank=True)
    gh_repositories = models.IntegerField(null=True, blank=True)
    gravatar_link = models.CharField(max_length=400, null=True, blank=True)

    def __str__(self):
        user = self.user
        return f'{user.first_name} {user.last_name} ({user.username})'


class Category(models.Model):
    class Meta:
        verbose_name_plural = "categories"

    label = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)

    def __str__(self):
        return f'{self.slug}'


class PostStatus(Enum):
    DRAFT = 'DRAFT'
    PUBLISHED = 'PUBLISHED'


POST_LABELED_STATUS = [
    (PostStatus.DRAFT.value, 'Draft'),
    (PostStatus.PUBLISHED.value, 'Published post'),
]


class Post(models.Model):
    title = models.CharField(max_length=400)
    body = models.TextField()
    image_link = models.CharField(max_length=400, null=True, blank=True)

    word_cloud_link = models.CharField(max_length=400, null=True, blank=True)

    source_link = models.CharField(max_length=400, null=True, blank=True)
    source_label = models.CharField(max_length=400, null=True, blank=True)

    status = models.CharField(
        max_length=32,
        choices=POST_LABELED_STATUS,
        default=PostStatus.DRAFT,
    )

    author = models.ForeignKey(CoolUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} - by {self.author.user.username}'
