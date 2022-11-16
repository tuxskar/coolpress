from django.test import TestCase, Client

from django.contrib.auth.models import User
from django.urls import reverse

from press.models import Category, Post, CoolUser, PostStatus


class PostPagesTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='oscar')
        cu = CoolUser.objects.create(user=user)
        category = Category.objects.create(label='Tech', slug='tech')
        titles = ['Awesome tech out new', 'Even greater news coming', 'Hello from the first Google IA']
        for title in titles:
            post = Post.objects.create(category=category, title=title, author=cu,
                                       status=PostStatus.PUBLISHED)

        titles = ['Secret news', 'Tesla is behind FTX']
        for title in titles:
            Post.objects.create(category=category, title=title, author=cu)
        cls.user = user
        cls.post = post
        cls.cu = cu

    def setUp(self):
        self.client = Client()

    def test_post_detail(self):
        response = self.client.get(reverse('posts-detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, 200)

    def test_posts(self):
        response = self.client.get(reverse('posts-list'))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.context['posts_list']), 3)


