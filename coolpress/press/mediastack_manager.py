import datetime
from typing import List

from django.contrib.auth.models import User
import requests

from coolpress.settings import MEDIASTACK_ACCESS_KEY
from press.models import Post, PostStatus, Category, CoolUser


def get_or_create_mediastack_author(r_json) -> CoolUser:
    names = (r_json.get('author') or 'anonymous').split()
    username = ''.join(names).lower()
    try:
        return CoolUser.objects.get(user__username=username)
    except CoolUser.DoesNotExist:
        first_name = names[0]
        last_name = ' '.join(names[1:])
        user = User.objects.create(username=username, first_name=first_name, last_name=last_name)
        return CoolUser.objects.create(user=user)


def get_or_create_mediastack_category(r_json) -> Category:
    label = r_json.get('category', 'general').title()
    try:
        return Category.objects.get(label=label)
    except Category.DoesNotExist:
        slug = label.replace(' ', '-').lower()
        return Category.objects.create(label=label, slug=slug)


def get_post_publish_time(r_json) -> datetime:
    return datetime.datetime.fromisoformat(r_json['published_at'])


def serialize_from_mediastack(response_json) -> Post:
    body = f"{response_json.get('description', '')}\nsee more at: {response_json.get('url', '')}"
    title = response_json.get('title', 'No Title')
    category = get_or_create_mediastack_category(response_json)
    image_link = response_json.get('image', '')
    try:
        return Post.objects.get(body=body, title=title, category=category, image_link=image_link)
    except Post.DoesNotExist:
        cu = get_or_create_mediastack_author(response_json)
        publish_date = get_post_publish_time(response_json)
        return Post.objects.create(title=title,
                                   body=body,
                                   image_link=image_link,
                                   status=PostStatus.PUBLISHED,
                                   author=cu,
                                   category=category,
                                   publish_date=publish_date)


def get_mediastack_posts(sources: List[str] = None, date: datetime.datetime = None,
                         languages: List[str] = None, keywords: List[str] = None,
                         categories: List[str] = None,
                         countries: List[str] = ['us'],
                         access_key=MEDIASTACK_ACCESS_KEY):
    params = {}
    if sources:
        params['sources'] = ','.join(sources)
    if date:
        formatter = '%Y-%m-%d'
        params['date'] = date.strftime(formatter)
    if languages:
        params['languages'] = ','.join(languages)
    if keywords:
        params['keywords'] = ','.join(keywords)
    if categories:
        params['categories'] = ','.join(categories)
    if countries:
        params['countries'] = ','.join(countries)
    params['access_key'] = access_key
    url = f'http://api.mediastack.com/v1/news'
    response = requests.get(url, params=params)
    json_returned = response.json()
    posts = []
    for response_json_post in json_returned.get('data', []):
        post = serialize_from_mediastack(response_json_post)
        posts.append(post)
    return posts
