from toolbox import S as Object

from ...bot import ShardedBotInstance



class ConfigProcessor(object):
    def __init__(self, bot: ShardedBotInstance):
        self.bot = bot
        self.configs = {}


    def get_config(self, guild_id: int) -> Object:
        return Object(
            self.db.configs.get_doc(guild_id)
        )


    def merge_config(self, guild_id: int) -> None:
        config = self.get_config(guild_id)
