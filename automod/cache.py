# type: ignore

import logging; log = logging.getLogger(__name__)
from typing import Union, List, Dict, Any, Optional
import os



class InternalCacheStore:
    def __init__(self, _type: str, bot) -> None:
        self.bot = bot
        self._type = _type
        self.data = {}
        for i in (getattr(self.bot.db, self._type)).find({}):
            if not str(i["id"]) in self.data:
                self.data[str(i["id"])] = i
        log.info(
            "[Database] Cached {}/{} documents from {}".format(
                len(self.data),
                len(list((getattr(self.bot.db, self._type)).find({}))),
                self._type
            ), 
            extra={"loc": f"PID {os.getpid()}"}
        )


    def get(self, _id: Union[str, int], key: str) -> Optional[Union[str, int, Dict[Union[str, int], Any], List[Any]]]:
        try:
            r = self.data[str(_id)].get(key, None)
        except KeyError:
            r = (getattr(self.bot.db, self._type)).get_from_db(_id, key)
            if r is not None:
                self.data[_id].update({
                    key: r
                }) 
        finally:
            return r


    def exists(self, _id: Union[str, int]) -> bool:
        return str(_id) in self.data


    def update(self, _id: Union[str, int], key: str, value: Union[str, int, Dict[Union[str, int], Any], List[Any]]) -> None:
        if str(_id) in self.data:
            self.data[str(_id)].update({
                key: value
            })


    def insert(self, _id: Union[str, int], schema: Dict[str, Any]) -> None:
        if not str(_id) in self.data:
            self.data[str(_id)] = schema


    def get_all(self, _id: Union[str, int]) -> Optional[dict]:
        if str(_id) in self.data:
            return self.data[str(_id)]
        return None


    def delete(self, _id: Union[str, int]) -> None:
        if str(_id) in self.data:
            del self.data[str(_id)]


class InternalCache:
    def __init__(self, bot) -> None:
        self.bot = bot
        for i in bot.config.cache_options:
            setattr(self, i, InternalCacheStore(i, bot))


    def new(self) -> None:
        for i in self.bot.config.cache_options:
            setattr(self, i, InternalCacheStore(i, self.bot))