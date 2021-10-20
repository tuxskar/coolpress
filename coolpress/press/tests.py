from django.contrib.auth.models import User
from django.test import TestCase

from press.models import CoolUser, Post, Category, PostStatus
from press.stats_manager import StatsDict, extract_posts_stats, word_cloud_to_filename


class UserManagementTest(TestCase):

    def test_creation_of_user(self):
        random_user = User.objects.create(username='randomtestUser', email='tuxskar@gmail.com')
        user = CoolUser.objects.create(user=random_user, github_profile='tuxskar')
        self.assertIsNot(user.gravatar_link, None)
        self.assertGreater(user.gh_repositories, 0)

    def test_modify_user_email_keep_same_gravatar_link(self):
        random_user = User.objects.create(username='randomtestUser', email='tuxskar@gmail.com')
        user = CoolUser.objects.create(user=random_user, github_profile='tuxskar')
        self.assertIsNot(user.gravatar_link, None)
        previous_gravatar_link = user.gravatar_link
        random_user.email = 'newwrongemail@gmail.com'
        random_user.save()
        self.assertEqual(user.gravatar_link, previous_gravatar_link)

    def test_creation_of_fake_user(self):
        random_user = User.objects.create(username='randomtestUser',
                                          email='pepito@noemailandrandom.com')
        user = CoolUser.objects.create(user=random_user, github_profile='epythonista')
        self.assertIs(user.gravatar_link, None)
        self.assertEqual(user.gh_repositories, 0)

    def test_creation_incorrect(self):
        random_user = User.objects.create(username='randomtestUser',
                                          email='juanita@noemailandrandom.com')
        user = CoolUser.objects.create(user=random_user, github_profile='someevenmorerandomuser')
        self.assertIs(user.gravatar_link, None)
        self.assertEqual(user.gh_repositories, None)


class StatsManagementTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='juanito', first_name='Juan', last_name='Perez')
        cu = CoolUser.objects.create(user=user)
        tech_category = Category.objects.create(slug='tech', label='Technology')
        events_category = Category.objects.create(slug='events', label='Events')
        categories = [tech_category, tech_category, events_category]
        for title, body, category in zip(TITLES, BODIES, categories):
            post = Post.objects.create(title=title, author=cu, category=category,
                                       status=PostStatus.PUBLISHED.value, body=body)
            post.save()

        cls.tech_category = tech_category

    def test_stats_dict(self):
        msg = 'This is just an example of how to manage the stats of a message'
        stats = StatsDict.from_msg(msg)
        self.assertEqual(stats.top(0), {})
        self.assertEqual(stats.top(1), {'of': 2})
        self.assertEqual(stats.top(2), {'of': 2, 'This': 1})
        self.assertEqual(stats.top(4), {'of': 2, 'This': 1, 'a': 1, 'an': 1})

    def test_stats_post(self):
        posts = Post.objects.filter(pk=1)
        post_stats = extract_posts_stats(posts)

        self.assertEqual(post_stats.titles.top(2), {'2021': 1, 'IDEs': 1})
        self.assertEqual(post_stats.bodies.top(2), {'to': 8, 'a': 6})
        self.assertEqual(post_stats.all.top(4), {'to': 8, 'a': 6, 'and': 6, 'IDE': 5})

    def test_category_stats(self):
        category = self.tech_category
        posts = Post.objects.filter(category=category)
        post_stats = extract_posts_stats(posts)

        self.assertEqual(post_stats.titles.top(2), {'Python': 2, '20': 1} )
        self.assertEqual(post_stats.bodies.top(2), {'to': 16, 'a': 10})
        self.assertEqual(post_stats.all.top(5), {'to': 16, 'a': 10, 'the': 9, 'of': 8, 'and': 7})

    def test_global_stats(self):
        pass  # to be done by the students

    def test_word_cloud_creation(self):
        category = self.tech_category
        posts = Post.objects.filter(category=category)
        post_stats = extract_posts_stats(posts)

        for vals, filename in ((post_stats.titles, 'press/test_titles_wc.jpg'),
                               (post_stats.bodies, 'press/test_bodies_wc.jpg'),
                               (post_stats.all, 'press/test_all_wc.jpg'),
                               ):
            new_filename = word_cloud_to_filename(vals, filename)
            self.assertIsNot(new_filename, None)

            self.assertIsNot(vals.word_cloud_svg(), None)



TITLES = [
    'Python IDEs in 2021',
    'Zen of Python – PEP 20',
    'Review of Clean Code – Robert Martin'

]

BODIES = [
    """An Integrated Development Environment (IDE) is a tool that helps to develop software applications. Each IDE is focused on some areas and most of them are designed to develop on a specific programming language. It is the tool to create applications easily.

The main features that each developer would seek when choosing an IDE are:

Ability to edit code.
Code execution on the same IDE.
Intuitive and user-friendly UI (User Interface).
Good support to find documentation of the libraries and frameworks used.
As you may already know, there are as many IDEs as tastes and there are language like Python that doesn’t even require an IDE to develop some application due that just writing a simple module, it can be run and have a small application, but when developing some extra features or big projects, a proper IDE is your best friend.

The main purpose of an IDE should be to help developers to develop faster, more efficient, more confident and in a more efective way.""",
    """Like in any other discipline, building software is in many cases, a matter of tastes. Depending on the developer background and the experiences it has, the code produced would be different in many aspects, leading usually to a heterogeneous styles to resolve the same problems using code.

In order to have some rules to have kind of similar code in Python when developers are trying to resolve the same kind of issues, it was written the Zen of Python, that is a set of rules to help developers to decide how to write code as a proper Pythonista.""",
    """Review and summary of Clean Code
    Clean Code has become a reference book for the programmers around the world. It explains some techniques and concepts that would allow us to improve our programming skills making our code more maintainable and scalable. Also it provides many examples on how to improve some code and pieces of code on how to transform it.
    
    Robert C Martin has dedicated several decades to study the rules to create clean code, helping programming teams and managing big applications to be maintainable so his knowledge on the field is quite extensive and it is shown on this book.
    
    The code examples are written in Java but they are simple and clear, so they can be followed by any programmer. Although it is recommended to make a slow and careful reading because the there are many details showed on each example, so grab a coffee and crush the book """
]
