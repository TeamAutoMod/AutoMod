import discord

import asyncio
import logging
import datetime

from plugins.Types import Embed
from . import Shell



log = logging.getLogger(__name__)

_bot = None

class BotUtils:
    def __init__(self, bot):
        self.bot = bot
        self.error_log = None
        self.shard_log = None
        self.last_fetches = {}
        self.shard_log_colors  = {
            "connect": 0x5cff9d,
            "resume": 0xffdc5c,
            "disconnect": 0xff5c5c
        }
        global _bot
        _bot = bot
    


    async def getMember(self, guild, user_id):
        cache_result = self.bot.cache.members.get(guild, user_id)
        if cache_result is not None and isinstance(cache_result, discord.Member):
            return cache_result
        else:
            if user_id in self.last_fetches:
                return self.last_fetches[user_id]
            
            fetched = discord.utils.get(guild.members, id=int(user_id))
            if fetched is not None:
                self.last_fetches[user_id] = fetched
                return fetched
            else:
                return None



    async def getUser(self, user_id):
        cache_result = self.bot.cache.users.get(user_id)
        if cache_result is not None and isinstance(cache_result, discord.User) or isinstance(cache_result, discord.Member):
            return cache_result
        else:
            if user_id in self.last_fetches:
                return self.last_fetches[user_id]
            
            fetched = discord.utils.get(self.bot.users, id=int(user_id))
            if fetched is not None:
                self.last_fetches[user_id] = fetched
                return fetched
            else:
                return None



    async def getChannel(self, guild, channel_id):
        cache_result = self.bot.cache.text_channels.get(guild, channel_id)
        if cache_result is not None and isinstance(cache_result, discord.TextChannel):
            return cache_result
        else:
            if channel_id in self.last_fetches:
                return self.last_fetches[channel_id]
            
            fetched = discord.utils.get(guild.text_channels, id=int(channel_id))
            if fetched is not None:
                self.last_fetches[channel_id] = fetched
                return fetched
            else:
                return None



    async def getRole(self, guild, role_id):
        cache_result = self.bot.cache.roles.get(guild, role_id)
        if cache_result is not None and isinstance(cache_result, discord.Role):
            return cache_result
        else:
            if role_id in self.last_fetches:
                return self.last_fetches[role_id]
            
            fetched = discord.utils.get(guild.roles, id=int(role_id))
            if fetched is not None:
                self.last_fetches[role_id] = fetched
                return fetched
            else:
                return None



    async def cleanShutdown(self):
        log.info("Bot is shutting down...")
        try:
            for t in asyncio.all_tasks():
                try:
                    t.cancel()
                except:
                    continue
        except RuntimeError:
            pass
        try:
            self.bot.run(self.bot.close())
            self.bot.loop.stop()
            self.bot.loop.close()
        except:
            pass
        quit(1)



    async def getVersion(self):
        _, output, __ = await Shell.run("git rev-parse --short FETCH_HEAD")
        return output



    def newCase(self, guild, _type, target, mod, reason):
        case_id = self.bot.db.configs.get(guild.id, "cases")
        case_id += 1

        timestamp = f"<t:{round(datetime.datetime.utcnow().timestamp())}>"

        self.bot.db.inf.insert(self.bot.schemas.Infraction(case_id, guild.id, target, mod, timestamp, _type, reason))
        self.bot.db.configs.update(guild.id, "cases", case_id)

        case_ids = self.bot.db.configs.get(guild.id, "case_ids")
        case_ids.update({
            f"{case_id}": {
                "mod": f"{mod.id}",
                "user": f"{target.id}",
                "guild": f"{guild.id}"
            }
        })
        self.bot.db.configs.update(guild.id, "case_ids", case_ids)

        return case_id



    async def dmUser(self, message, _type, user, **kwargs):
        e = Embed(
            color=kwargs.get("color"),
            description=self.bot.i18next.translate(message.guild, f"{_type}_dm", **kwargs)
        )
        e.add_field(
            name="❯ Reason",
            value=kwargs.get("reason", "No reason"),
            inline=True
        )
        e.add_field(
            name="❯ Moderator",
            value=f"{kwargs.get('moderator')}" if self.bot.db.configs.get(message.guild.id, "show_mod_in_dm") == True else "Hidden",
            inline=True
        )
        res = ""
        state = self.bot.db.configs.get(message.guild.id, "dm_on_actions")
        if state is True:
            try:
                await user.send(embed=e)
                res += "(user notified with a direct message)"
            except Exception:
                res += "(failed to message user)"
            finally:
                return res
        else:
            return ""


    async def sendErrorLog(self, embed):
        if self.error_log is None:
            self.error_log = await self.bot.fetch_channel(self.bot.config.error_log_channel)
        await self.error_log.send(embed=embed)


    async def sendShardLog(self, event, shard_id):
        e = Embed(
            color=self.shard_log_colors[event],
            description=self.bot.i18next.get(f"log_{event}", shard_id=shard_id)
        )
        if self.shard_log is None:
            self.shard_log = await self.bot.fetch_channel(self.bot.config.shard_log_channel)
        await self.shard_log.send(embed=e)

