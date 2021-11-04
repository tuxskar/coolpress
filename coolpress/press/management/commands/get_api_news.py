from django.core.management import BaseCommand

from press.mediastack_manager import gather_and_create_news


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('categories', nargs='+', help='The categories to be pulled information from')
        parser.add_argument('--limit', type=int, help='Limit of posts to be added')

    def handle(self, *args, **options):
        limit = options['limit']
        categories = options['categories']
        singles_categories = []
        for cat in categories:
            if ',' in cat:
                singles_categories.extend(cat.split(','))
            else:
                singles_categories.append(cat)
        inserted_posts = gather_and_create_news(singles_categories, ['en'], limit)

        self.stdout.write(f'Inserted {len(inserted_posts)} posts of news about {singles_categories} out of the limit {limit}')