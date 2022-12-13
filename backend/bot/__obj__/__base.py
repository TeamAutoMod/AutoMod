import json

from .__types import _PY_TYPES_DISCORD_POSSIBLE_ITER
from typing import Dict



class TypeHintedToolboxObject:
    def __init__(self, data: Dict[str, _PY_TYPES_DISCORD_POSSIBLE_ITER] = {}) -> None:
        self._raw = data
        class _(dict):
            def __init__(self, *args, **kwargs):
                super(_, self).__init__(*args, **kwargs)
                self.__dict__ = self
            
            @classmethod
            def nested(cls, data):
                if not isinstance(data, dict):
                    return data
                else:
                    return cls({k: cls.nested(data[k]) for k in data})

        for k, v in _.nested(data).items():
            if str(k).isdigit():
                raise Exception(f"Keys have to be strict strings, not possible integers - Error with: {k}")
            else:
                setattr(self, str(k), v)
    

    def __len__(self) -> int:
        return len([x for x in dir(self) if not x.startswith("_")])
    

    def __repr__(self) -> str:
        return json.dumps(self._raw, separators=(',', ':'))
    

    def __getattr__(self, k: str) -> _PY_TYPES_DISCORD_POSSIBLE_ITER:
        try:
            return self._raw[k]
        except KeyError:
            raise
    

    def _new(self, new=None) -> None:
        self.__init__(new or self._raw)