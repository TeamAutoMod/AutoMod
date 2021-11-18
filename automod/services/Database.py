from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

import logging; log = logging.getLogger(__name__)
import datetime



class CollectionCache:
    def __init__(self, _type, collection):
        self.collection = collection
        self.data = {}
        if _type != "stats":
            for i in collection.find({}):
                if not str(i["id"]) in self.data:
                    self.data.update(
                        {
                            str(i["id"]): i
                        }
                    )


    def get(self, _id, key):
        try:
            r = self.data[str(_id)].get(key, None)
        except KeyError:
            r = self.collection.actual_get(_id, key)
            if r is not None:
                self.data[_id].update({
                    key: r
                }) 
        finally:
            return r


    def exists(self, _id):
        return str(_id) in self.data


    def update(self, _id, key, value):
        if str(_id) in self.data:
            self.data[str(_id)].update({
                key: value
            })
            self.collection.actual_update(_id, key, value)


    def insert(self, schema):
        _id = schema["id"]
        if not str(_id) in self.data:
            self.data[str(_id)] = schema


    def get_doc(self, _id):
        if str(_id) in self.data:
            return self.data[str(_id)]
        else:
            return self.collection.actual_get_doc(_id)


    def delete(self, _id):
        if str(_id) in self.data:
            del self.data[str(_id)]



class MongoCollection(Collection):
    def __init__(self, database, name, **kwargs):
        super().__init__(database, name, **kwargs)
        self.key = "id"
        #self._cache = CollectionCache(name, self)

    
    def i_get(self, v, k):
        self._cache.get(v, k)

    
    def exists(self, _id):
        found = [x for x in super().find({f"{self.key}": f"{_id}"})]
        if len(found) <= 0 or found == "":
            return False
        else:
            return True


    def i_update(self, _id, key, value):
        self._cache.update(_id, key, value)


    def i_get_doc(self, _id):
        return self._cache.get_doc(_id)

    
    def insert(self, schema):
        #self._cache.insert(schema)
        super().insert_one(schema)


    def delete(self, filter_value):
        #self._cache.delete(filter_value)
        super().delete_one({f"{self.key}": f"{filter_value}"})


    def get(self, filter_value, key):
        if isinstance(filter_value, int):
            filter_value = str(filter_value)
        try:
            for _ in super().find({f"{self.key}": f"{filter_value}"}):
                return _[f"{key}"]
        except Exception:
            return None

    
    def update(self, filter_value, key, new_value):
        super().update_one({f"{self.key}": f"{filter_value}"}, {"$set": {f"{key}": new_value}}, upsert=False)


    def update_stats(self, filter_value, updates):
        super().update_one({f"{self.key}": f"{filter_value}"}, {"$set": {"messages": updates}}, upsert=False)


    def get_doc(self, filter_value):
        try:
            return list(super().find({f"{self.key}": f"{filter_value}"}))[0]
        except Exception:
            return None





class MongoDatabase(Database):
    def __init__(self, client, name, **kwargs):
        super().__init__(client, name, **kwargs)

        self.configs = MongoCollection(self, "guildconfigs")
        self.ranks = MongoCollection(self, "ranks")
        self.tags = MongoCollection(self, "tags")
        self.warns = MongoCollection(self, "warns")
        self.mutes = MongoCollection(self, "mutes")
        self.inf = MongoCollection(self, "infractions")
        self.persists = MongoCollection(self, "persists")
        self.follows = MongoCollection(self, "follows")
        self.stars = MongoCollection(self, "stars")

        self.stats = MongoCollection(self, "stats") # this is just experimental



class MongoDB(MongoClient):
    def __init__(self, host=None, port=None, _name=None, **kwargs):
        log.info("Connecting to database")
        super().__init__(host=host, port=port, **kwargs)
        self.database = MongoDatabase(self, _name)


    def get(self):
        return self.database



class MongoSchemas:
    def __init__(self, bot):
        self.bot = bot
        pass


    def Tag(self, tag_id, reply, author, created):
        schema = {
            "id": f"{tag_id}",
            "reply": f"{reply}",
            "author": f"{author.id}",
            "created": created,
            "last_edited": None,
            "edited_by": "",
            "uses": 0
        }
        return schema


    def Warn(self, warn_id, warns: int):
        schema = {
            "id": f"{warn_id}",
            "warns": warns
        }
        return schema


    def Follow(self, follow_id, user_id):
        schema = {
            "id": f"{follow_id}",
            "users": [user_id]
        }
        return schema

    
    def Persist(self, guild_id, user_id, roles, nickname):
        schema = {
            "id": f"{guild_id}-{user_id}",
            "roles": roles,
            "nick": f"{nickname}"
        }
        return schema


    def GuildConfig(self, guild):
        prefix = self.bot.config.default_prefix
        schema = { 
            "id": f"{guild.id}", 
            "prefix": "{}".format(prefix if prefix != "" or prefix != None else "!"), 
            "mute_role": "",

            "mod_log": "", 
            "message_log": "",
            "server_log": "",
            "voice_log": "", 

            "antispam": False,
            "server_logging": False,
            "message_logging": False,
            "voice_logging": False,
            "persist": False,
            "dm_on_actions": False,
            "show_mod_in_dm": False,

            "ignored_channels": [],
            "ignored_roles": [],
            "whitelisted_invites": [],

            "punishments": {},

            "automod": {},

            "filters": {},

            "embed_role": "",
            "emoji_role": "",
            "tag_role": "",

            "cases": 0,
            "case_ids": {},

            "starboard": {
                "enabled": False,
                "channel": "",
                "ignored_channels": []
            },

            "pre_reasons": {},

            "lang": "en_US",
            "guild_name": f"{guild.name}",
        }
        return schema


    def Level(self, guild_id, user_id):
        schema = {
            "id": f"{guild_id}-{user_id}",
            "lvl": 1,
            "xp": 0
        }
        return schema


    def Mute(self, guild_id, user_id, ending_date):
        schema = {
            "id": f"{guild_id}-{user_id}",
            "ending": ending_date
        }
        return schema


    def Infraction(self, case_id, guild_id, target, moderator, timestamp, inf_type, reason):
        schema = {
            "id": f"{guild_id}-{case_id}",
            "case": f"{case_id}",
            "guild": f"{guild_id}",
            "target": f"{target.name}#{target.discriminator}",
            "target_id": f"{target.id}",
            "moderator": f"{moderator.name}#{moderator.discriminator}",
            "moderator_id": f"{moderator.id}",
            "timestamp": timestamp,
            "type": f"{inf_type}",
            "reason": f"{reason}",
            "target_av": f"{target.display_avatar}",
            "moderator_av": f"{moderator.display_avatar}",
            "log_id": "",
            "jump_url": ""
        }
        return schema


    def StarboardEntry(self, message):
        schema = {
            "id": f"{message.id}",
            "guild": f"{message.guild.id}",
            "channel": f"{message.channel.id}",
            "author": f"{message.author.id}",
            "log_message": "",
            "stars": 1
        }
        return schema


    def UserStats(self, _id):
        schema = {
            "id": f"{_id}",
            "messages": {
                "first": datetime.datetime.utcnow(),
                "last": datetime.datetime.utcnow(),

                "total_sent": 0,
                "total_deleted": 0,

                "total_emotes": 0,
                "total_pings": 0,
                "total_attachments": 0,

                "used_emotes": {},
                "most_used_emote": {
                    "name": "",
                    "id": "",
                    "used": 0
                }
            },
            "voice": {
                "sessions": 0,
                "total_time": 0,
            }
        }
        return schema