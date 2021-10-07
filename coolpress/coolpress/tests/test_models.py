from django.test import TestCase

from django.contrib.auth.models import User

from press.models import Post, CoolUser, Category, PostStatus


class PostModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='juanito', first_name='Juan', last_name='Perez')
        cu = CoolUser.objects.create(user=user)
        category = Category.objects.create(slug='random', label='Some random news')
        post = Post.objects.create(title='The great testing news',
                                   author=cu, category=category, status=PostStatus.PUBLISHED.value,
                                   body='This story is fake, but as there are fake news is as credible and legitimate as any other')
        cls.user = user
        cls.cu = cu
        cls.category = category
        cls.post = post

    def test_check_last_update_updates(self):
        old_last_update = self.post.last_update
        self.post.title = 'New title super cool'
        self.post.save()
        new_last_update = self.post.last_update
        self.assertGreater(new_last_update, old_last_update)

    def test_post_object_name(self):
        post = Post.objects.get(id=1)
        expected_object_name = f'{post.title} - by {post.author.user.username}'
        self.assertEquals(expected_object_name, str(post))

    def test_category_object_name(self):
        cat = Category.objects.get(id=1)
        expected_object_name = f'{cat.slug}'
        self.assertEquals(expected_object_name, str(cat))

    def test_cooluser_object_name(self):
        user = self.user
        expected_object_name = f'{user.first_name} {user.last_name} ({user.username})'
        self.assertEquals(expected_object_name, str(self.cu))
