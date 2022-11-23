from enum import Enum
from libgravatar import Gravatar
from django.contrib.auth.models import User
from django.db import models


class CoolUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gravatar_link = models.URLField(null=True, blank=True)
    github_profile = models.CharField(max_length=300, null=True, blank=True)
    gh_repositories = models.IntegerField(null=True, blank=True)
    last_update = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        if self.user.email is not None:
            self.gravatar_link = Gravatar(self.user.email).get_image()
        self.gh_repositories = self.get_github_repos()
        self.last_update = models.DateTimeField(auto_now=True)
        super(CoolUser, self).save(*args, **kwargs)


class Category(models.Model):
    class Meta:
        verbose_name_plural = 'categories'

    label = models.CharField(max_length=200)
    slug = models.SlugField()

    def __str__(self):
        return f'{self.label} ({self.id})'


class PostStatus(Enum):
    DRAFT = 'DRAFT'
    PUBLISHED = 'PUBLISHED'


class Post(models.Model):
    title = models.CharField(max_length=400)
    body = models.TextField(null=True)
    image_link = models.URLField(null=True)
    status = models.CharField(max_length=32,
                              choices=[(PostStatus.DRAFT, 'DRAFT'),
                                       (PostStatus.PUBLISHED, 'PUBLISHED')],
                              default=PostStatus.DRAFT)

    author = models.ForeignKey(CoolUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class CommentStatus:
    PUBLISHED = 'PUBLISHED'
    NON_PUBLISHED = 'NON_PUBLISHED'


class Comment(models.Model):
    body = models.TextField()
    status = models.CharField(max_length=32,
                              choices=[(CommentStatus.PUBLISHED, 'Published'),
                                       (CommentStatus.NON_PUBLISHED, 'Non Published')],
                              default=CommentStatus.PUBLISHED)
    votes = models.IntegerField()

    author = models.ForeignKey(CoolUser, on_delete=models.DO_NOTHING)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.body[:10]} - from: {self.author.user.username}'
