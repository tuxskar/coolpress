import json
import os.path
from collections import Counter

from django.db.models import QuerySet
from wordcloud import WordCloud

from press.models import Post

from press.models import Comment

with open(os.path.join(os.path.dirname(__file__), 'stopwords.json')) as fr:
    file_stopwords = json.load(fr)
    STOPWORDS = set(file_stopwords)
    STOPWORDS.add('"')
    STOPWORDS.add('.')
    STOPWORDS.add('-')


class Stats:
    def __init__(self, text):
        self.text = text

    def _analyze(self):
        words = self.text.lower().replace(',', ' ').replace('\n', ' ').split(' ')
        words = filter(lambda x: len(x) > 0 and not x.isdigit() and not x.isspace()
                                 and x not in STOPWORDS, words)
        return Counter(words)

    def top(self, limit=1):
        if limit < 0:
            raise ValueError()

        analyzed = self._analyze()
        results = sorted(analyzed.items(),
                         key=lambda key_val: (-key_val[1], key_val[0]))
        return results[:limit]

    @property
    def word_cloud(self, limit=0):
        top_words = self.top(20)
        if len(top_words) != 0:
            return WordCloud(colormap='Greens').generate_from_frequencies(dict(top_words))
        return


def posts_analyzer(qs_post: QuerySet[Post], limit=1):
    post_qs_titles = qs_post.values_list('title', flat=True)
    post_qs_bodies = qs_post.values_list('body', flat=True)
    post_titles = ' '.join(post_qs_titles)
    post_bodies = ' '.join(post_qs_bodies)
    full_msg = f'{post_titles} {post_bodies}'
    st = Stats(full_msg)
    return st


def comments_analyzer(qs_comments: QuerySet[Comment], limit=0):
    comment_body = qs_comments.values_list("body", flat=True)
    comment_bodies = ' '.join(comment_body)
    comment_stats = Stats(comment_bodies)
    return comment_stats
