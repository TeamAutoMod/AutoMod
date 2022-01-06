import discord
from discord.ext import commands

import json
import traceback
import requests
from toolbox import S as Object
import logging; log = logging.getLogger()

from .cache import InternalCache
from .mongo import MongoDB
from .schemas import GuildConfig
from .utils import Translator, Emotes
from .types import Context
from .views import pages



def prefix_callable(bot, msg):
    default = [f"<@!{bot.user.id}> ", f"<@{bot.user.id}> "] # when the bot is mentioned
    if msg.guild is None:
        default.append(bot.config.default_prefix)
    else:
        try:
            prefix = bot.cache.configs.get(msg.guild.id, "prefix")
            default.append(prefix)
        except Exception:
            default.append(bot.config.default_prefix)

    for p in default:
        if p == None: default.remove(p) # sometimes a prefix is still None and without this check it'll throw an error
    
    return default


class ShardedBotInstance(commands.AutoShardedBot):
    intents = discord.Intents(
        guilds=True,
        members=True,
        bans=True,
        emojis=True,
        messages=True,
        reactions=True,
        typing=False
    )
    def __init__(self, *args, **kwargs):
        with open("backend/config.json", "r", encoding="utf8", errors="ignore") as config_file:
            self.config = Object(json.load(config_file))
        super().__init__(
            command_prefix=prefix_callable, intents=self.intents, 
            case_insensitive=True, max_messages=1000, chunk_guilds_at_startup=False, 
            allowed_mentions=discord.AllowedMentions(everyone=False, replied_user=False),
            *args, **kwargs
        )
        pages.inject_bot_obj(self)

        self.ready = False
        self.locked = False

        self.used_commands = 0
        self.used_tags = 0

        self.command_stats = {}
        self.ignore_for_events = []
        self.case_cmd_cache = {}

        self.db = MongoDB(self)
        self.cache = InternalCache(self)
        self.emotes = Emotes(self)
        self.locale = Translator(self)

        self.load_plugins()
        self.run()


    async def on_ready(self):
        if self.config.custom_status != "":
            if self.activity == None: await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=self.config.custom_status))

        if not self.ready:
            for g in self.guilds:
                if not self.db.configs.exists(g.id):
                    self.db.configs.insert(GuildConfig(g, self.config.default_prefix))
            
            self.ready = True

    
    async def on_message(self, msg: discord.Message):
        if msg.author.bot or msg.guild is None:
            return
        ctx = await self.get_context(msg, cls=Context)
        if ctx.valid and ctx.command is not None:
            self.used_commands += 1
            if not ctx.command.qualified_name in self.command_stats:
                self.command_stats.update({
                    ctx.command.qualified_name: 1
                })
            else:
                self.command_stats[ctx.command.qualified_name] += 1
            if self.ready:
                if not msg.guild.chunked:
                    await msg.guild.chunk(cache=True)
            
            await self.invoke(ctx)
            
    
    def load_plugins(self):
        try:
            self.remove_command("help")
        except Exception:
            pass
        finally:
            for p in self.config.plugins: self.load_plugin(p)
            self.plugins = self.cogs


    def register_plugin(self, plugin):
        super().add_cog(plugin)


    def load_plugin(self, plugin):
        try:
            super().load_extension(f"backend.plugins.{plugin}")
        except Exception:
            log.error(f"Failed to load {plugin} - {traceback.format_exc()}")
        else:
            log.info(f"Successfully loaded {plugin}")


    def get_plugin(self, name):
        return super().get_cog(name)


    def handle_timeout(self, mute, guild, user, iso8601_ts):
        exc = ""
        try:
            resp = requests.patch(
                f"https://discord.com/api/v9/guilds/{guild.id}/members/{user.id}",
                json={
                    "communication_disabled_until": None if mute == False else iso8601_ts
                }, 
                headers={
                    "Authorization": f"Bot {self.config.token}"
                }
            )
            if resp.status_code != 200: exc = resp.text
        except Exception as ex:
            log.warn(f"Error while trying to mute user ({user.id}) (guild: {guild.id}) - {ex}"); exc = ex
        finally:
            return exc


    def run(self):
        try:
            super().run(self.config.token, reconnect=True)
        finally:
            for h in log.handlers[:]: h.close(); log.removeHandler(h)