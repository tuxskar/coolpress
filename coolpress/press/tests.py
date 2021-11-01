import os

from django.contrib.auth.models import User
from django.test import TestCase, Client

# Create your tests here.
from django.urls import reverse

from press.models import Category, CoolUser, Post
from press.stats_manager import StatsDict, extract_stats_from_single_post
from press.user_management import get_gravatar_link, extract_github_repositories


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
        self.assertTrue(gravatar_link,
                        'https://www.gravatar.com/avatar/139f76ac09f8b9d3a2392b45b7ad5f4c')

    def test_get_gravatar_negative(self):
        gravatar_link = get_gravatar_link(self.wrong_email)
        self.assertIsNone(gravatar_link)


class GithubManager(TestCase):

    @classmethod
    def setUpTestData(cls):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        sample_path = '__tests_data__/sample_github_profile.html'
        full_path = os.path.join(dir_path, sample_path)
        with open(full_path, 'r') as fr:
            cls.sample_content = fr.read().encode()
        cls.proper_email = 'tuxskar@gmail.com'

    def test_unit_extract_repositories_from_sample(self):
        repositories_cnt = extract_github_repositories(self.sample_content)
        self.assertEqual(repositories_cnt, 34)

    def test_get_github_repositories(self):
        random_user = User.objects.create(username='randomUser', email=self.proper_email)
        cool_user = CoolUser.objects.create(user=random_user, github_profile='tuxskar')
        self.assertGreaterEqual(cool_user.gh_repositories, 1)

    def test_get_github_repositories_of_random_account(self):
        random_user = User.objects.create(username='randomUser', email=self.proper_email)
        cool_user = CoolUser.objects.create(user=random_user,
                                            github_profile='tuxskar_some_random_username')
        self.assertEqual(cool_user.gh_repositories, None)

    def test_github_repositories_updating(self):
        random_user = User.objects.create(username='randomUser', email=self.proper_email)
        cool_user = CoolUser.objects.create(user=random_user,
                                            github_profile='tuxskar_some_random_username')
        self.assertEqual(cool_user.gh_repositories, None)

        cool_user.github_profile = 'tuxskar'
        cool_user.save()

        self.assertGreaterEqual(cool_user.gh_repositories, 34)

        cool_user.github_profile = 'tuxskar_some_random_username'
        cool_user.save()
        self.assertEqual(cool_user.gh_repositories, None)


class StatsManager(TestCase):
    def test_stats_sample(self):
        msg = 'science ' * 3 + 'art ' * 7 + 'cats ' * 7 + 'of ' * 10 + 'a ' * 10
        sd = StatsDict.from_msg(msg)
        self.assertEqual(sd.top(1), {'a': 10})
        self.assertEqual(sd.top(2), {'a': 10, 'of': 10})
        self.assertEqual(sd.top(10), {'a': 10, 'of': 10, 'art': 7, 'cats': 7, 'science': 3, '': 1})
        from_sd = sd.top(5)
        self.assertEqual(from_sd.top(2), {'a': 10, 'of': 10})

    def test_single_post(self):
        title = 'Applied Python Module because python is awesome, yes it is'
        body = 'This is a description of the module just for fun and to sew how it looks ' \
               'like like like like or subscribe'
        sample_post = Post(title=title, body=body)
        stats = extract_stats_from_single_post(sample_post)

        self.assertEqual(stats.titles.top(2), {'is': 2, 'python': 2})
        self.assertEqual(stats.bodies.top(1), {'like': 4})
        self.assertEqual(stats.all.top(1), {'like': 4})
