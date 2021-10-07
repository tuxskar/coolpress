from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from press.forms import PostForm
from press.models import CoolUser, Category, Post, PostStatus


class FormsPostTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_pass = 'pythonisthebest'
        active_user = User.objects.create(username='elpythonista', first_name='Oscar',
                                          last_name='Ramirez', is_active=True)
        active_user.set_password(cls.test_pass)
        active_user.save()

        cls.active_cu = CoolUser.objects.create(user=active_user)

        inactive_user = User.objects.create(username='pepita', first_name='Juana',
                                            last_name='De Arco', is_active=False)
        cls.inactive_cu = CoolUser.objects.create(user=inactive_user)
        category = Category.objects.create(slug='random', label='Some random news')
        cls.inactive_post = Post.objects.create(
            title='The great testing news',
            author=cls.inactive_cu, category=category,
            status=PostStatus.DRAFT.value,
            body='Even if inactive a user need to express itself')

        cls.active_post = Post.objects.create(
            title='The great testing from the active user',
            author=cls.active_cu, category=category,
            status=PostStatus.PUBLISHED.value,
            body='An active user writting something cool')

    def setUp(self):
        self.client = Client()

    def test_inactive_user_cant_create_posts(self):
        response = self.client.get(reverse('post-add'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(
            reverse('post-update', kwargs=dict(post_id=self.inactive_post.id)))
        self.assertEqual(response.status_code, 302)
        login = self.client.login(username=self.active_cu.user.username, password=self.test_pass)
        response = self.client.get(reverse('post-add'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('post-update', kwargs=dict(post_id=self.active_post.id)))
        self.assertEqual(response.status_code, 200)

        # Although logged the user is not the same as the author so can't be changed
        response = self.client.get(
            reverse('post-update', kwargs=dict(post_id=self.inactive_post.id)))
        self.assertEqual(response.status_code, 400)

    def test_post_form_correct(self):
        form_data = {'title': 'GREAT TITLE', 'category': 1, 'status': 'DRAFT',
                     'body': 'Some great news have great content, this one not'}
        form = PostForm(data=form_data)
        is_valid = form.is_valid()
        self.assertTrue(is_valid)

    def test_post_form_incorrect(self):
        form_data = {'title': 'GREAT TITLE', 'category': 1, 'status': 'RANDOMSTATUS!',
                     'body': 'Some great news have great content, this one not'}
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['status'][0],
                         'Select a valid choice. RANDOMSTATUS! is not one of the available choices.')

    def test_create_a_post_with_author_authenticated(self):
        login = self.client.login(username=self.active_cu.user.username, password=self.test_pass)
        prev_cnt_post = Post.objects.count()
        title = 'GREAT TITLE TESTING CLIENT'
        form_data = {'title': title, 'category': 1, 'status': 'DRAFT',
                     'body': 'Some great news have great content, this one not'}
        response = self.client.post(reverse('post-add'), data=form_data)
        new_cnt_post = Post.objects.count()
        self.assertEqual(prev_cnt_post + 1, new_cnt_post)
        created_post = Post.objects.filter(title=title, author=self.active_cu).exists()
        self.assertEqual(created_post, True)
