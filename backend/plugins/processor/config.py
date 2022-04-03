from toolbox import S as Object



class ConfigProcessor(object):
    def __init__(self, bot):
        self.bot = bot
        self.configs = {}


    def get_config(self, guild_id):
        return Object(
            self.db.configs.get_doc(guild_id)
        )


    def merge_config(self, guild_id):
        config = self.get_config(guild_id)
