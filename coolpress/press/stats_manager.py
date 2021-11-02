from collections import Counter
from dataclasses import dataclass

from django.db.models import QuerySet

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


@dataclass
class Stats:
    titles: StatsDict
    bodies: StatsDict

    @property
    def all(self):
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
