import datetime
from enum import Enum

import requests
import bs4
from libgravatar import Gravatar
from django.contrib.auth.models import User
from django.db import models
from pyparsing import Optional


class CoolUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gravatar_link = models.URLField(null=True, blank=True)
    github_profile = models.CharField(max_length=300, null=True, blank=True)
    gh_repositories = models.IntegerField(null=True, blank=True)
    gh_stars = models.IntegerField(null=True, blank=True)

    gravatar_updated_at = models.DateTimeField(auto_now=False, blank=True)

    def save(self, *args, **kwargs):
        if self.user.email is not None:
            gravatar_link = Gravatar(self.user.email).get_image()
            if gravatar_link != self.gravatar_link:
                self.gravatar_updated_at = datetime.datetime.utcnow()
        self.gh_repositories = self.get_github_repos()
        self.gh_stars = self.get_github_stars()
        super(CoolUser, self).save(*args, **kwargs)

    def get_github_url(self):
        if self.github_profile:
            url = f'https://github.com/{self.github_profile}'
            response = requests.get(url)
            if response.status_code == 200:
                return url

    def get_github_repos(self):
        url = self.get_github_url()
        if url:
            response = requests.get(url)
            soup = bs4.BeautifulSoup(response.content, 'html.parser')
            css_selector = '.Counter'
            repositories_info = soup.select_one(css_selector)
            repos_text = repositories_info.text
            return int(repos_text)

    def get_github_stars(self):
        url = self.get_github_url()
        if url:
            response = requests.get(url)
            soup = bs4.BeautifulSoup(response.content, 'html.parser')
            css_selector = 'body > div.application-main > main > div.mt-4.position-sticky.top-0.d-none.d-md-block.color-bg-default.width-full.border-bottom.color-border-muted > div > div > div.Layout-main > div > nav > a:nth-child(5) > span'
            stars_info = soup.select_one(css_selector)
            repos_text = stars_info.text
            return int(repos_text)


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
    commentcounter = 0


    def CommentCounter(self):
        self.commentcounter += 1

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
