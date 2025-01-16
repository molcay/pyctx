from typing import List

from .helpers import JsonObject

__all__ = ["ContextData",]

class ContextData(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._data: JsonObject = {}

    def _find_and_set(self, key, value, d: JsonObject = None) -> None:
        if d is None:
            d = self._data

        parts: List[str] = key.split('/')
        first_part: str = parts[0]

        if len(parts) < 2:
            d[first_part] = value
            return

        if first_part not in d:
            d[first_part] = {}

        return self._find_and_set("/".join(parts[1:]), value, d[first_part])

    def flat(self) -> JsonObject:
        for key, value in self.items():
            self._find_and_set(key, value)

        return self._data
