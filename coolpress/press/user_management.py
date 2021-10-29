from typing import Optional

from libgravatar import Gravatar
from pip._vendor import requests


def get_gravatar_link(email: str) -> Optional[str]:
    g = Gravatar(email)
    profile_url = g.get_profile()
    response = requests.get(profile_url)
    if response.status_code == 200:
        return profile_url
