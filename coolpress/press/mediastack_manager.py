import os
from typing import List

import requests
from django.contrib.auth.models import User

from press.models import Post, Category, CoolUser, PostStatus


def insert_post_from_mediastack(single_post):
    title = single_post.get('title')
    body = single_post.get('description')
    category = get_or_create_category(single_post.get('category'))
    author = get_or_create_author(single_post.get('author'), single_post.get('source'))

    already_exists = Post.objects.filter(title=title, author=author, category=category).exists()
    if already_exists:
        return None
    else:
        image_link = single_post.get('image')
        return Post.objects.create(category=category, author=author, title=title,
                                   body=body, image_link=image_link,
                                   status=PostStatus.PUBLISHED.value)


def get_or_create_category(ms_category) -> Category:
    slug_cat = ms_category.lower() if ms_category else 'general'
    try:
        cat = Category.objects.get(slug=slug_cat)
    except Category.DoesNotExist as e:
        label = f'{ms_category.capitalize()} News'
        cat = Category.objects.create(slug=slug_cat, label=label)
    return cat


def get_or_create_author(ms_author_name, ms_source):
    username = get_author_username(ms_author_name, ms_source)

    try:
        cu = CoolUser.objects.get(user__username=username)
    except CoolUser.DoesNotExist:
        first_name = ms_author_name or 'anonymous'
        user = User.objects.create(username=username, email=username,
                                   first_name=first_name)
        cu = CoolUser.objects.create(user=user)
    return cu


def get_author_username(author_name, source):
    username = 'anonymous'
    if author_name:
        if 'staff' in author_name.lower():
            username = 'staff'
        else:
            names = author_name.split(' ')
            if len(names) == 1:
                username = author_name
            else:
                first_letter = author_name[0]
                last_name = names[-1]
                username = f'{first_letter}{last_name}'
            username = username.lower()
    domain = source.lower() if source and source.endswith('.com') else 'coolpress.com'
    return f'{username}@{domain}'


def gather_and_create_news(categories, languages, limit) -> List[Post]:
    api_key = os.environ['MEDIASTACK_API']
    base_url = 'http://api.mediastack.com/v1/news'
    params = {'limit': limit,
              'languages': ','.join(languages),
              'categories': ','.join(categories),
              'access_key': api_key,
              'sort': 'published_desc',
              }
    response = requests.get(base_url, params=params)
    post_list = []
    for ms_post in response.json()['data']:
        post = insert_post_from_mediastack(ms_post)
        if post:
            post_list.append(post)
    return post_list
