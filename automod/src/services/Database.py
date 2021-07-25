from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

import logging



log = logging.getLogger(__name__)

class MongoCollection(Collection):
    def __init__(self, database, name, **kwargs):
        super().__init__(database, name, **kwargs)
        self.key = "id"


    def get(self, filter_value, key):
        if isinstance(filter_value, int):
            filter_value = str(filter_value)
        try:
            for _ in super().find({f"{self.key}": f"{filter_value}"}):
                return _[f"{key}"]
        except Exception:
            return None


    def insert(self, schema):
        super().insert_one(schema)

    
    def update(self, filter_value, key, new_value):
        super().update({f"{self.key}": f"{filter_value}"}, {"$set": {f"{key}": new_value}}, upsert=False, multi=False)

    
    def delete(self, filter_value):
        super().delete_one({f"{self.key}": f"{filter_value}"})


    def exists(self, filter_value):
        found = [x for x in super().find({f"{self.key}": f"{filter_value}"})]
        if len(found) <= 0 or found == "":
            return False
        else:
            return True


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



class MongoDB(MongoClient):
    def __init__(self, host=None, port=None, **kwargs):
        log.info("Connecting to database")
        super().__init__(host=host, port=port, **kwargs)
        self.database = MongoDatabase(self, "main")


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

            "ignored_channels": [],
            "ignored_roles": [],
            "whitelisted_invites": [],

            "punishments": {},

            "automod": {},

            "filters": {},

            "embed_role": "",
            "emoji_role": "",
            "tag_role": "",

            "lang": "en_US",
            "cases": 0,
            "guild_name": f"{guild.name}"
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
            "target_av": f"{target.avatar_url_as()}",
            "moderator_av": f"{moderator.avatar_url_as()}",
            "log_id": ""
        }
        return schema