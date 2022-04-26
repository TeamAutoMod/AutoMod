import logging; log = logging.getLogger(__name__)
from typing import Union, TypeVar



T = TypeVar("T", str, dict, int, list)
DB_ID = TypeVar("DB_ID", str, int)


class InternalCacheStore(object):
    def __init__(self, _type: str, bot) -> None:
        self.bot = bot
        self._type = _type
        self.data = {}
        for i in (getattr(self.bot.db, self._type)).find({}):
            if not str(i["id"]) in self.data:
                self.data[str(i["id"])] = i
        log.info(
            "📁 Cached {}/{} documents from {}".format(
                len(self.data),
                len(list((getattr(self.bot.db, self._type)).find({}))),
                self._type
            )
        )


    def get(self, _id: DB_ID, key) -> Union[T, None]:
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


    def exists(self, _id: DB_ID) -> bool:
        return str(_id) in self.data


    def update(self, _id: DB_ID, key: str, value: T) -> Union[T, None]:
        if str(_id) in self.data:
            self.data[str(_id)].update({
                key: value
            })


    def insert(self, _id: DB_ID, schema: dict) -> None:
        if not str(_id) in self.data:
            self.data[str(_id)] = schema


    def get_all(self, _id: DB_ID) -> Union[dict, None]:
        if str(_id) in self.data:
            return self.data[str(_id)]
        return None


    def delete(self, _id: DB_ID) -> None:
        if str(_id) in self.data:
            del self.data[str(_id)]


class InternalCache(object):
    def __init__(self, bot) -> None:
        self.bot = bot
        for i in bot.config.cache_options:
            setattr(self, i, InternalCacheStore(i, bot))


    def new(self) -> None:
        for i in self.bot.config.cache_options:
            setattr(self, i, InternalCacheStore(i, self.bot))