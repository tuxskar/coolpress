from collections import Counter
from dataclasses import dataclass

import numpy as np
from django.db.models import QuerySet

from wordcloud import WordCloud, STOPWORDS
from press.models import Post


class StatsDict(dict):

    def top(self, limit=10):
        return self._get_top(self, limit)

    @staticmethod
    def _get_top(dict_to_limit, limit=10):
        sorted_items = sorted(dict_to_limit.items(), key=lambda item: (-item[1], item[0]))
        keys = [key for key, val in sorted_items][:limit]
        top_dict = StatsDict()
        for key in keys:
            value = dict_to_limit[key]
            top_dict[key] = value

        return top_dict

    @classmethod
    def from_msg(cls, msg: str):
        tokens = msg.casefold().split(' ')
        return cls(**Counter(tokens))


    def weighted_dict(self):
        new_dict = {}
        for word, cnt in self.items():
            if word not in STOPWORDS:
                new_weight = len(word) * cnt
                new_word = word.replace(',', '')
                new_dict[new_word] = new_weight
        return StatsDict(**new_dict)

    def get_word_cloud(self, limit=10):
        x, y = np.ogrid[:300, :300]

        mask = (x - 150) ** 2 + (y - 150) ** 2 > 130 ** 2
        mask = 255 * mask.astype(int)

        wc = WordCloud(background_color='white', mask=mask)
        weighted_dict = self.weighted_dict()
        top_values = self._get_top(weighted_dict, limit)
        wc.fit_words(top_values)
        return wc

    def to_file(self, file_path, limit=10):
        wc = self.get_word_cloud(limit)
        wc.to_file(file_path)
        return file_path

    def to_svg(self, limit=10):
        wc = self.get_word_cloud(limit)
        return wc.to_svg()

@dataclass
class Stats:
    titles: StatsDict
    bodies: StatsDict

    @property
    def all(self) -> StatsDict:
        return StatsDict({**self.titles, **self.bodies})


def extract_stats_from_single_post(post: Post) -> Stats:
    posts_query = Post.objects.filter(id=post.id)
    return extract_stats_from_posts(posts_query)


def extract_stats_from_posts(qs_post: QuerySet[Post]) -> Stats:
    titles_list = qs_post.values_list('title', flat=True)
    titles_msg = ' '.join(titles_list)
    bodies_list = qs_post.values_list('body', flat=True)
    bodies_msg = ' '.join(bodies_list)
    titles = StatsDict.from_msg(titles_msg)
    bodies = StatsDict.from_msg(bodies_msg)
    return Stats(titles, bodies)
