from collections import Counter


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
