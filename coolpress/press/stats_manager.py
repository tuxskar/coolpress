from collections import Counter
from dataclasses import dataclass

from django.db.models import QuerySet
from wordcloud import WordCloud

from press.models import Post


class StatsDict(dict):

    def top(self, limit=10):
        return self._get_top(self, limit)

    @staticmethod
    def _get_top(dict_to_limit: dict, limit=10):
        sorted_items = sorted(dict_to_limit.items(), key=lambda item: (-item[1], item[0]))
        keys = [key for key, val in sorted_items][:limit]
        top_dict = StatsDict()
        for key in keys:
            value = dict_to_limit[key]
            top_dict[key] = value

        return top_dict

    @classmethod
    def from_msg(cls, msg: str):
        tokens = msg.split(' ')
        return cls(**Counter(tokens))

    def word_cloud(self, limit=15):
        freqs_weighted = get_weighted_frequencies(self)
        top_weighted_values = self._get_top(freqs_weighted, limit)
        wc = WordCloud()
        wc.fit_words(top_weighted_values)
        return wc

    def word_cloud_svg(self, limit=15):
        wc = self.word_cloud(limit)
        return wc.to_svg()


@dataclass
class Stats:
    titles: StatsDict
    bodies: StatsDict

    @property
    def all(self):
        return StatsDict({**self.titles, **self.bodies})


def extract_posts_stats(posts: QuerySet[Post]):
    titles = posts.values_list('title', flat=True)
    bodies = posts.values_list('body', flat=True)
    if not titles and not bodies:
        return None

    titles_msgs = ' '.join(titles)
    bodies_msgs = ' '.join(bodies)
    titles_stats = StatsDict.from_msg(titles_msgs)
    bodies_stats = StatsDict.from_msg(bodies_msgs)
    return Stats(titles=titles_stats, bodies=bodies_stats)


def get_weighted_frequencies(text_frequencies: StatsDict):
    weighted = {}
    for key, value in text_frequencies.items():
        value = len(key) or 1
        if 3 < len(key) < 15:
            value = len(key) ** 2
        elif len(key) >= 15:
            value = 1
        weighted[key] = value
    return weighted


def word_cloud_to_filename(text_frequencies: StatsDict, filename):
    # This would be an exercise for the students
    wc = text_frequencies.word_cloud()
    wc.to_file(filename)
    return filename
