from collections import Counter
from dataclasses import dataclass

from django.db.models import QuerySet

from press.models import Post


class StatsDict(dict):

    def top(self, limit=10):
        sorted_items = sorted(self.items(), key=lambda item: (-item[1], item[0]))
        keys = [key for key, val in sorted_items][:limit]
        top_dict = {}
        for key in keys:
            value = self[key]
            top_dict[key] = value

        return top_dict

    @classmethod
    def from_msg(cls, msg: str):
        tokens = msg.split(' ')
        return cls(**Counter(tokens))


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
    titles_msgs = ' '.join(titles)
    bodies_msgs = ' '.join(bodies)
    titles_stats = StatsDict.from_msg(titles_msgs)
    bodies_stats = StatsDict.from_msg(bodies_msgs)
    return Stats(titles=titles_stats, bodies=bodies_stats)