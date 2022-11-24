from django.core.management import BaseCommand

from press.mediastack_manager import get_mediastack_posts


class Command(BaseCommand):
    help = 'Get the latest news from mediastack'

    def add_arguments(self, parser):
        parser.add_argument('categories', nargs='*', type=str)
        parser.add_argument('sources', nargs='*', type=str)

    def handle(self, *args, **options):
        sources = options['sources']
        categories = options['categories']

        posts = get_mediastack_posts(sources=sources, categories=categories)

        self.stdout.write(f'Saved {len(posts)} new posts for {sources} sources and {categories} categories')
