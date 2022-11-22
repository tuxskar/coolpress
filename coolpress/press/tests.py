from django.test import TestCase

from django.contrib.auth.models import User

# Create your tests here.
from press.models import CoolUser, Post, Category
from press.stats_manager import Stats, posts_analyzer


class UserManagementTest(TestCase):
    def test_creation_of_user(self):
        random_user = User.objects.create(username='pepitosuperpro',
                                          email='random@example.com')
        cu = CoolUser.objects.create(user=random_user)
        random_avatar = 'https://www.gravatar.com/avatar/d6d904021bf50ecbc3c4f1f5394aa578'
        self.assertEqual(cu.gravatar_link, random_avatar)

        random_user.email = 'tuxskar@gmail.com'
        random_user.save()
        cu.save()
        proper_avatar = 'https://www.gravatar.com/avatar/139f76ac09f8b9d3a2392b45b7ad5f4c'
        self.assertEqual(cu.gravatar_link, proper_avatar)


class UserGitHubUpdates(TestCase):
    def test_gather_github_repos(self):
        random_user = User.objects.create(username='pepitosuperpro',
                                          email='random@example.com')
        cu = CoolUser.objects.create(user=random_user,
                                     github_profile='tuxskar')
        self.assertEqual(cu.gh_repositories, 36)
        self.assertEqual(cu.get_github_url(), 'https://github.com/tuxskar')

    def test_gather_github_no_repos(self):
        random_user = User.objects.create(username='pepitosuperpro2',
                                          email='random@example.com')
        cu = CoolUser.objects.create(user=random_user,
                                     github_profile='ytuyiopiytdfghjkyresdjnbnkfdfghjk')
        self.assertEqual(cu.gh_repositories, None)
        self.assertEqual(cu.get_github_url(), None)

    def test_gather_github_no_profile(self):
        random_user = User.objects.create(username='pepitosuperpro1',
                                          email='random@example.com')
        cu = CoolUser.objects.create(user=random_user,
                                     github_profile=None)
        self.assertEqual(cu.gh_repositories, None)
        self.assertEqual(cu.get_github_url(), None)


class StatsManager(TestCase):
    def test_analyze_text_stats(self):
        text = 'Hello hello harbour'
        expected = [('hello', 2), ('harbour', 1)]
        s = Stats(text)
        self.assertEqual(s.top(2), expected)
        self.assertEqual(s.top(20), expected)

    def test_analyze_text_stats_side_effects(self):
        text = 'Hello hello harbour Harbour bye'
        expected = [('harbour', 2), ('hello', 2), ('bye', 1)]
        s = Stats(text)
        expected_for_1 = expected[:1]
        self.assertEqual(s.top(), expected_for_1)
        self.assertEqual(s.top(1), expected_for_1)
        self.assertEqual(s.top(0), [])
        with self.assertRaises(ValueError):
            results = s.top(-3)

    def test_analyze_text_avoid_stopwords(self):
        text = 'Hello hello a the and in on he of is to from     everyone harbour Harbour bye'
        expected = [('harbour', 2), ('hello', 2), ('bye', 1)]
        s = Stats(text)
        actual = s.top(20)
        self.assertEqual(actual, expected)

    def test_stats_on_actual_news(self):
        text = """
        Elon Musk sent a flurry of emails to Twitter employees on Friday morning with a plea.

“Anyone who actually writes software, please report to the 10th floor at 2 p.m. today,” he wrote in a two-paragraph message, which was viewed by The New York Times. “Thanks, Elon.”

About 30 minutes later, Mr. Musk sent another email saying he wanted to learn about Twitter’s “tech stack,” a term used to describe a company’s software and related systems. Then in another email, he asked some people to fly to Twitter’s headquarters in San Francisco to meet in person.

Twitter is teetering on the edge as Mr. Musk remakes the company after buying it for $44 billion last month. The billionaire has pushed relentlessly to put his imprint on the social media service, slashing 50 percent of its work force, firing dissenters, pursuing new subscription products and delivering a harsh message that the company needs to shape up or it will face bankruptcy.

Now the question is whether Mr. Musk, 51, has gone too far. On Thursday, hundreds of Twitter employees resigned after Mr. Musk gave them a deadline to decide whether to leave or stay. So many workers chose to depart that Twitter users began questioning whether the site would survive, tweeting farewell messages to the service and turning hashtags like #TwitterMigration and #TwitterTakeover into trending topics.
        """
        ex = [('harbour', 2), ('hello', 2), ('bye', 1)]
        s = Stats(text)
        self.assertEqual(s.top(), [('musk', 5)])
        self.assertEqual(s.top(5),
                         [('musk', 5), ('mr.', 4), ('twitter', 4), ('company', 2), ('email', 2)])


class PostStatsManager(TestCase):
    def test_single_post_stats(self):
        user = User.objects.create(username='oscar')
        cu = CoolUser.objects.create(user=user)
        post = Post.objects.create(category=Category.objects.create(label='Tech', slug='tech'),
                                   title='Hello this is our first test',
                                   body='In this particular test we are counting the words',
                                   author=cu)
        expected = [('test', 2)]
        post_queryset = Post.objects.filter(id=post.id)
        stats = posts_analyzer(post_queryset)

        self.assertEqual(stats.top(1), expected)
