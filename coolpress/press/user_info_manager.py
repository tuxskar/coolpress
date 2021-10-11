from typing import Optional

import requests
from libgravatar import Gravatar
from bs4 import BeautifulSoup


def get_gravatar_image(email) -> Optional[str]:
    """Only will return a url if the user exists and is correct on gravatar, otherwise None"""
    g = Gravatar(email)
    profile_url = g.get_profile()
    res = requests.get(profile_url)
    if res.status_code == 200:
        return g.get_image()
    return None


def get_github_repositories(github_username):
    """Only will return a url if the user exists and will return the number of repositories,
     even if there are none will return 0"""
    url = f'https://github.com/{github_username}'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        css_selector = 'div.UnderlineNav > nav > a:nth-child(2) > span'
        try:
            repositories_info = soup.select_one(css_selector)
            return int(repositories_info.text)
        except AttributeError:
            pass
