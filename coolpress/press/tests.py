from django.contrib.auth.models import User
from django.test import TestCase

from press.models import CoolUser


class UserManagementTest(TestCase):

    def test_creation_of_user(self):
        random_user = User.objects.create(username='randomtestUser', email='tuxskar@gmail.com')
        user = CoolUser.objects.create(user=random_user, github_profile='tuxskar')
        self.assertIsNot(user.gravatar_link, None)
        self.assertGreater(user.gh_repositories, 0)

    def test_creation_of_fake_user(self):
        random_user = User.objects.create(username='randomtestUser',
                                          email='pepito@noemailandrandom.com')
        user = CoolUser.objects.create(user=random_user, github_profile='epythonista')
        self.assertIs(user.gravatar_link, None)
        self.assertEqual(user.gh_repositories, 0)
