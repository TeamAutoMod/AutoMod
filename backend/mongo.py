from toolbox import Database, Collection



class MongoCollection(Collection):
    def __init__(self, bot, database, name):
        super().__init__(database=database, name=name)
        self.bot = bot
        self.collection_name = name
        self.cached = name in bot.config.cache_options


    def get(self, _id, key):
        return (getattr(self.bot.cache, self.collection_name)).get(_id, key)

    
    def get_from_db(self, _id, key):
        return super().get(_id, key)


    def insert(self, schema):
        super().insert(schema)
        if self.cached: (getattr(self.bot.cache, self.collection_name)).insert(schema)


    def update(self, _id, key, value):
        super().update(_id, key, value)
        if self.cached: (getattr(self.bot.cache, self.collection_name)).update(_id, key, value)


    def multi_update(self, _id, updates: dict):
        for k, v in updates.items():
            self.update(_id, k, v)


    def delete(self, _id):
        super().delete(_id)
        if self.cached: (getattr(self.bot.cache, self.collection_name)).delete(_id)
            

class MongoDB(Database):
    def __init__(self, bot):
        super().__init__(name=bot.config.db_name, host=bot.config.mongo_host)
        for obj_name, db_name in {
            "configs": "guildconfigs",
            "tags": "tags",
            "cases": "cases",
            "warns": "warns",
            "mutes": "mutes"
        }.items():
            setattr(self, obj_name, MongoCollection(bot, self, db_name))