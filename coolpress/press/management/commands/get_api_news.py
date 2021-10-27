import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from pip._vendor import requests

from press.config import MEDIASTACK_API
from press.models import Post, CoolUser, Category, PostStatus


class Command(BaseCommand):
    help = 'Get the latest news from mediastack'

    def add_arguments(self, parser):
        parser.add_argument('categories', nargs='+', type=str)

        parser.add_argument(
            '--limit',
            action='store',
            help='Change the default 10 news per execution',
            default=10,
            type=int
        )

    def handle(self, *args, **options):
        categories = options['categories']
        limit = options['limit']

        added = get_and_insert_posts(categories, limit)

        self.stdout.write(self.style.SUCCESS(
            f'Successfully added {len(added)} new news for categories {categories}'))


def get_and_insert_posts(categories, limit, api_key=MEDIASTACK_API):
    response = get_mediastack_news(categories, limit, api_key)
    response_data = response.json()['data']
    added = insert_posts_response_data(response_data)
    return added


def get_mediastack_news(categories, limit, api_key):
    params = {
        'access_key': api_key,
        'categories': ','.join(categories),
        'sort': 'published_desc',
        'limit': limit,
        'languages': 'en'
    }
    url = 'http://api.mediastack.com/v1/news'
    response = requests.get(url, params=params)
    return response


def insert_posts_response_data(response_data):
    added = []
    for info in response_data:
        inserted_post = insert_post(info)
        if inserted_post:
            added.append(inserted_post)
    return added


def insert_post(post_info):
    title = post_info['title']
    author = get_or_create_author(post_info)
    category = get_or_create_category(post_info)
    already_exist = Post.objects.filter(title=title, author=author, category=category).exists()
    if not already_exist:
        author = get_or_create_author(post_info)
        post = Post(title=title, author=author, body=post_info['description'],
                    source_label=post_info['source'], image_link=post_info['image'],
                    category=category, source_link=post_info['url'],
                    status=PostStatus.PUBLISHED.value)
        post.save()
        return post


def get_or_create_category(post_info):
    slug = post_info['category']
    try:
        category = Category.objects.get(slug=slug)
    except Category.DoesNotExist as e:
        category = Category.objects.create(slug=slug, label=slug.capitalize())
    return category


def get_or_create_author(post_info):
    author_info = post_info.get('author') or 'anonymous'
    return get_or_create_cool_user_from_author(author_info)


def get_or_create_cool_user_from_author(author_info):
    if ',' in author_info:
        author_info = author_info.split(',')[0]

    first_name = author_info.replace('(', '').replace(')', '')
    last_name = ''
    if 'Staff' in author_info:
        fake_domain = author_info.replace('Staff', '').strip()
        email = f'info@{fake_domain.lower()}.com'
    else:
        words = author_info.split()
        if len(words) > 1:
            first_name = words[0]
            last_name = ' '.join(words[1:])
            username = words[0][0] + ''.join(words[1:])
        else:
            username = first_name
        email = f'{username}@noemail.com'.lower()

    username = email
    try:
        return CoolUser.objects.get(user__username=username)
    except CoolUser.DoesNotExist:
        user = User(first_name=first_name, email=email, username=username, last_name=last_name,
                    is_staff=False, is_active=False)
    cu = CoolUser(user=user)
    user.save()
    cu.save()
    return cu
