from django.contrib.auth.models import User
from django.test import TestCase, Client

# Create your tests here.
from django.urls import reverse

from press.models import Category, CoolUser, Post


class PostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u = User.objects.create(first_name='juanito')
        cls.cu = CoolUser.objects.create(user=cls.u)
        cls.cat = Category.objects.create(slug='random', label='Some random news')
        cls.p = Post.objects.create(category=cls.cat, author=cls.cu)

    def test_sample_post(self):
        self.assertEqual(self.cu.pk, 1)

        cnt_of_post = Post.objects.count()
        self.assertEqual(cnt_of_post, 1)

    def test_post_detail(self):
        client = Client()
        url = reverse('posts-detail', kwargs={'post_id': self.p.pk})
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['post_obj'], self.p)
        url = '/post/pepe'
        response = client.get(url)
        self.assertEqual(response.status_code, 404)
        url = reverse('posts-detail', kwargs={'post_id': 10})
        response = client.get(url)
        self.assertEqual(response.status_code, 404)


class CreatePostUsingForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.juan = User.objects.create(first_name='juanito', is_active=True, username='juanito')
        cls.cu = CoolUser.objects.create(user=cls.juan)
        cls.cat = Category.objects.create(slug='random', label='Some random news')
        cls.juan_post = Post.objects.create(category=cls.cat, author=cls.cu)

        cls.juan_pass = 'Holamundo'
        cls.juan.set_password('Holamundo')
        cls.juan.save()

        cls.maria = User.objects.create(first_name='maria', is_active=True, username='maria')
        cls.cu = CoolUser.objects.create(user=cls.maria)

        cls.maria_pass = 'HolamundoMaria'
        cls.maria.set_password(cls.maria_pass)
        cls.maria.save()

    def setUp(self):
        self.client = Client()

    def test_check_others_updating_permissions(self):
        update_juan_post = reverse('post-update', kwargs=dict(post_id=self.juan_post.id))
        # is_logged_in = self.client.login(usename=self.juan.username, password='Holamundo')
        is_logged = self.client.force_login(self.juan, backend=None)

        response = self.client.get(update_juan_post)
        self.assertEqual(response.status_code, 200)

        is_logged = self.client.force_login(self.maria, backend=None)
        response = self.client.get(update_juan_post)
        self.assertEqual(response.status_code, 400)
