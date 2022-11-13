# Checking that when there are posts, the root is showing it

# Filtering by some category is only showing the one of that category - this one analyzing the DOM
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from coolpress.settings import HOME_INDEX
from press.models import CoolUser, Category, Post, PostStatus


class PostListTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='juanito', first_name='Juan', last_name='Valderrama')
        cu = CoolUser.objects.create(user=user)
        random_cat = Category.objects.create(slug='random', label='Some random news')
        tech_cat = Category.objects.create(slug='tech', label='Techie good content')

        posts = []
        for title, category in [('Tesla is launching a new power bank that last a year', tech_cat),
                                ('Apple will buy Tesla for an iPadRoadster', tech_cat),
                                ('Microsoft will finally launch a great OS', tech_cat),
                                ('Cats are not fighting dogs anymore', random_cat),
                                ]:
            post = Post.objects.create(title=title,
                                       author=cu, category=category,
                                       status=PostStatus.PUBLISHED.value,
                                       body=title * 10)
            posts.append(post)
            post = Post.objects.create(title=f'Unpublished {title}',
                                       author=cu, category=category,
                                       status=PostStatus.DRAFT.value,
                                       body=title * 10)
            posts.append(post)
        cls.user = user
        cls.cu = cu
        cls.tech_category = tech_cat
        cls.posts = posts

    def setUp(self):
        self.client = Client()

    def test_get_all_posts(self):
        response = self.client.get(reverse(HOME_INDEX))
        self.assertEqual(response.status_code, 200)
        # Check that the rendered context contains 5 customers.
        self.assertEqual(len(response.context['post_list']), 4)

    def test_get_only_techies(self):
        response = self.client.get(
            reverse('posts-list-by-category',
                    kwargs=dict(category_slug=self.tech_category.slug)))
        self.assertEqual(response.status_code, 200)
        # Check that the rendered context contains 5 customers.
        self.assertEqual(len(response.context['post_list']), 3)

    def test_get_missing_animals_category(self):
        response = self.client.get(
            reverse('posts-list-by-category',
                    kwargs=dict(category_slug='animals')))
        self.assertEqual(response.status_code, 404)

    def test_get_single_post(self):
        response = self.client.get(
            reverse('posts-detail',
                    kwargs=dict(post_id=self.posts[0].id)))
        self.assertEqual(response.status_code, 200)

    # Check non published posts are not shown
    # Check that non-authenticated users can reach the creation posts page
    # Check that non-published comments are hidden from the post-detail
    # Check that the comments are passed to the context of the post-detail
