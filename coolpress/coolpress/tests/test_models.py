from django.test import TestCase, Client

from django.contrib.auth.models import User

from press.models import Category, Post, CoolUser, PostStatus


class PostModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='oscar')
        cu = CoolUser.objects.create(user=user)
        post = Post.objects.create(category=Category.objects.create(label='Tech', slug='tech'),
                                   title='a new mac is out there',
                                   author=cu)
        cls.user = user
        cls.post = post
        cls.cu = cu

    def test_checking_post_representation(self):
        actual = str(self.post)

        expected = f'Tech: a new mac is out there'
        self.assertEqual(actual, expected)

    def test_creation_proper_post(self):
        self.assertEqual(self.post.status, PostStatus.DRAFT)
        username = self.post.author.user.username
        self.assertIsNotNone(username)
