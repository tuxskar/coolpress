from enum import Enum

from django.contrib.auth.models import User
from django.core.mail import mail_admins
from django.db import models
from django.urls import reverse

from press.user_info_manager import get_github_repositories, get_gravatar_image


class CoolUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    github_profile = models.CharField(max_length=150, null=True, blank=True)
    gh_repositories = models.IntegerField(null=True, blank=True)
    gravatar_link = models.CharField(max_length=400, null=True, blank=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} ({self.user.username})'

    def save(self, *args, **kwargs):
        super(CoolUser, self).save(*args, **kwargs)

        email = self.user.email
        if self.gravatar_link is None and email:
            image_link = get_gravatar_image(email)
            if image_link:
                self.gravatar_link = image_link
                self.save()
        if self.gh_repositories is None and self.github_profile:
            repositories = get_github_repositories(self.github_profile)
            if repositories is not None:
                self.gh_repositories = repositories
                self.save()


class Category(models.Model):
    class Meta:
        verbose_name_plural = "categories"

    label = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)

    def get_absolute_url(self):
        return reverse('posts-list-by-category', kwargs=dict(category_slug=self.slug))

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

    trigger_keyword = 'covid'.casefold()

    def __str__(self):
        return f'{self.title} - by {self.author.user.username}'

    def should_send_email(self):
        is_in_title = self.title and self.trigger_keyword in self.title.casefold()
        is_in_body = self.body and self.trigger_keyword in self.body.casefold()
        return is_in_title or is_in_body

    def get_absolute_url(self):
        return reverse('posts-detail', kwargs=dict(post_id=self.pk))

    def save(self, *args, **kwargs):
        super(Post, self).save(*args, **kwargs)
        if self.should_send_email():
            subject = f'Keyword {self.trigger_keyword} detected'

            body = f'Dear admin\n {subject} on the post {self.get_absolute_url()}'
            mail_admins(subject, body)
