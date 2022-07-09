from typing import Union, TypeVar
from toolbox import Database, Collection
import logging; log = logging.getLogger(__name__)



T = TypeVar("T", str, dict, int, list)
DB_ID = TypeVar("DB_ID", str, int)


class MongoCollection(Collection):
    def __init__(
        self, 
        bot, 
        database, name: str
    ) -> None:
        super().__init__(database=database, name=name)
        self.bot = bot
        self.collection_name = name
        self.cached = name in bot.config.cache_options


    def get(
        self, 
        _id: DB_ID, 
        key: str
    ) -> Union[
        T, 
        None
    ]:
        if self.cached:
            return (getattr(self.bot.cache, self.collection_name)).get(_id, key)
        else:
            return super().get(_id, key)

    def get_doc(
        self, 
        _id: DB_ID
    ) -> Union[
        dict, 
        None
    ]:
        if self.cached:
            return (getattr(self.bot.cache, self.collection_name)).get_all(_id)
        else:
            return super().get_doc(_id)


    def get_from_db(
        self, 
        _id: DB_ID, 
        key: str
    ) -> Union[
        T, 
        None
    ]:
        return super().get(_id, key)


    def insert(
        self, 
        schema: dict
    ) -> None:
        super().insert_one(schema)
        if self.cached: (getattr(self.bot.cache, self.collection_name)).insert(schema["id"], schema)


    def update(
        self, 
        _id: DB_ID, 
        key: str, 
        value: T
    ) -> None:
        super().update(_id, key, value)
        if self.cached: (getattr(self.bot.cache, self.collection_name)).update(_id, key, value)


    def multi_update(
        self, 
        _id: DB_ID, 
        updates: dict
    ) -> None:
        for k, v in updates.items():
            self.update(_id, k, v)


    def delete(
        self, 
        _id: DB_ID
    ) -> None:
        super().delete(_id)
        if self.cached: (getattr(self.bot.cache, self.collection_name)).delete(_id)


    def multi_delete(
        self, 
        _filter: dict
    ) -> None:
        super().delete_many(_filter)
        if self.cached:
            data = (getattr(self.bot.cache, self.collection_name)).data
            for k in (getattr(self.bot.cache, self.collection_name)).data.copy():
                if data[k][list(_filter.keys())[0]] == list(_filter.values())[0]:
                    (getattr(self.bot.cache, self.collection_name)).delete(k)


class MongoDB(Database):
    def __init__(
        self, 
        bot
    ) -> None:
        super().__init__(name=bot.config.db_name, host=bot.config.mongo_url)

        # Only doing this to have type hints
        self.configs = MongoCollection(bot, self, "configs")
        self.tags = MongoCollection(bot, self, "tags")
        self.cases = MongoCollection(bot, self, "cases")
        self.warns = MongoCollection(bot, self, "warns")
        self.mutes = MongoCollection(bot, self, "mutes")
        self.level = MongoCollection(bot, self, "level")
        self.slowmodes = MongoCollection(bot, self, "slowmodes")
        self.tbans = MongoCollection(bot, self, "tbans")
        
        log.info("📮 Database initialized")