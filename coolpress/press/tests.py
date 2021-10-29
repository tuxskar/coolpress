from django.contrib.auth.models import User
from django.test import TestCase, Client

# Create your tests here.
from django.urls import reverse

from press.models import Category, CoolUser, Post
from press.user_management import get_gravatar_link


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
        update_juans_post = reverse('post-update', kwargs=dict(post_id=self.juan_post.id))
        is_logged_in = self.client.login(username=self.juan.username, password=self.juan_pass)
        self.assertTrue(is_logged_in)

        response = self.client.get(update_juans_post)
        self.assertEqual(response.status_code, 200)

        is_logged_in = self.client.login(username=self.maria.username, password=self.maria_pass)
        self.assertTrue(is_logged_in)
        response = self.client.get(update_juans_post)
        self.assertEqual(response.status_code, 400)


class UserManagementTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.proper_email = 'tuxskar@gmail.com'
        cls.wrong_email = 'tuxksarAlotofRandomThings@gmailRandomGoogleWhyNot.com'

    def test_positive_creation_of(self):
        random_user = User.objects.create(username='randomUser', email=self.proper_email)
        user = CoolUser.objects.create(user=random_user)
        self.assertIsNotNone(user.gravatar_link)

    def test_negative_creation_of_gravatar_links(self):
        random_user = User.objects.create(username='randomUser', email=self.wrong_email)
        user = CoolUser.objects.create(user=random_user)
        self.assertIsNone(user.gravatar_link)

    def test_update_email(self):
        random_user = User.objects.create(username='randomUser', email=self.wrong_email)
        cool_user = CoolUser.objects.create(user=random_user)
        self.assertIsNone(cool_user.gravatar_link)

        cool_user.user.email = self.proper_email
        cool_user.save()
        self.assertIsNotNone(cool_user.gravatar_link)


    def test_get_gravatar_positive(self):
        gravatar_link = get_gravatar_link(self.proper_email)
        self.assertIsNotNone(gravatar_link)
        self.assertTrue(gravatar_link, 'https://www.gravatar.com/avatar/139f76ac09f8b9d3a2392b45b7ad5f4c')

    def test_get_gravatar_negative(self):
        gravatar_link = get_gravatar_link(self.wrong_email)
        self.assertIsNone(gravatar_link)
