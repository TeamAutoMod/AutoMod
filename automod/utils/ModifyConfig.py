import json
import pathlib



class ModifyConfig:
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config


    def block_guild(self, guild_id):
        with open(f"{pathlib.Path(__file__).parent.parent.parent}/config.json", "r", encoding="utf8", errors="ignore") as f:
            current = json.load(f)

            
            current["blocked_guilds"] = [guild_id, *current["blocked_guilds"]]

        with open(f"{pathlib.Path(__file__).parent.parent.parent}/config.json", "w", encoding="utf8", errors="ignore") as f:
            json.dump(current, f, indent=4)

        self.reload_config()


    def unblock_guild(self, guild_id):
        with open(f"{pathlib.Path(__file__).parent.parent.parent}/config.json", "r", encoding="utf8", errors="ignore") as f:
            current = json.load(f)

            current["blocked_guilds"] = list(filter(lambda x: x != guild_id, current["blocked_guilds"]))

        with open(f"{pathlib.Path(__file__).parent.parent.parent}/config.json", "w", encoding="utf8", errors="ignore") as f:
            json.dump(current, f, indent=4)

        self.reload_config()


    def reload_config(self):
        self.bot.config = json.load(open(f"{pathlib.Path(__file__).parent.parent.parent}/config.json", "r", closefd=True))
