import discord
from discord.ext import commands

import json
import traceback
import requests
import datetime
from toolbox import S as Object
import logging; log = logging.getLogger()

from .cache import InternalCache
from .mongo import MongoDB
from .schemas import GuildConfig
from .utils import Translator, Emotes
from .types import Context, embed
from .views import pages
from .observer import Observer



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
    __slots__ = [
        "config"

        "ready",
        "locked",
        "avatar_as_bytes",
        "uptime",
        "last_reload",

        "used_commands",
        "used_tags",

        "command_stats",
        "ignore_for_events",
        "case_cmd_cache",
        "webhook_cache",
        "fetched_user_cache",

        "db",
        "cache",
        "emotes",
        "locale"
    ]
    
    intents = discord.Intents(
        guilds=True,
        members=True,
        bans=True,
        emojis=True,
        messages=True,
        reactions=True,
        typing=False
    )
    if hasattr(intents, "message_content"):
        intents.message_content = True
    def __init__(self, *args, **kwargs):
        with open("backend/config.json", "r", encoding="utf8", errors="ignore") as config_file:
            self.config = Object(json.load(config_file))
        super().__init__(
            command_prefix=prefix_callable, intents=self.intents, 
            case_insensitive=True, max_messages=1000, chunk_guilds_at_startup=False, 
            allowed_mentions=discord.AllowedMentions(everyone=False, replied_user=False),
            *args, **kwargs
        )
        for f in [pages, embed]: f.inject_bot_obj(self)

        self.ready = False
        self.locked = False
        self.avatar_as_bytes = None
        self.uptime = datetime.datetime.utcnow()
        self.last_reload = datetime.datetime.utcnow().timestamp()

        self.used_commands = 0
        self.used_tags = 0

        self.command_stats = {}
        self.ignore_for_events = []
        self.case_cmd_cache = {}
        self.webhook_cache = {}
        self.fetched_user_cache = {}

        if self.config.watch == True:
            self.observer = Observer(self)
        self.db = MongoDB(self)
        self.cache = InternalCache(self)
        self.emotes = Emotes(self)
        self.locale = Translator(self)

        self.run()


    async def on_ready(self):
        if self.config.custom_status != "":
            if self.activity == None: await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=self.config.custom_status))

        if not self.ready:
            await self.load_plugins()
            if self.config.watch == True:
                await self.observer.start()
            for g in self.guilds:
                if not self.db.configs.exists(g.id):
                    self.db.configs.insert(GuildConfig(g, self.config.default_prefix))
            
            m = self.guilds[0].me
            if m != None:
                if m.avatar != None:
                    self.avatar_as_bytes = await m.avatar.read()
                else:
                    self.avatar_as_bytes = None
            self.ready = True

    
    async def on_message(self, msg: discord.Message):
        if msg.author.bot or msg.guild is None:
            return
        ctx = await self.get_context(msg, cls=Context)
        if ctx.valid and ctx.command is not None:
            self.used_commands += 1
            disabled = self.db.configs.get(msg.guild.id, "disabled_commands")
            if ctx.command.name.lower() in disabled:
                if ctx.author.guild_permissions.manage_messages == False:
                    try:
                        await msg.add_reaction(
                            self.emotes.get("LOCK")
                        )
                    except Exception:
                        pass
                    finally:
                        return
            
            if self.ready:
                if not msg.guild.chunked:
                    await msg.guild.chunk(cache=True)
            
            await self.invoke(ctx)
            
    
    async def load_plugins(self):
        try:
            self.remove_command("help")
        except Exception:
            pass
        finally:
            for p in self.config.plugins: 
                await self.load_plugin(p)
            self.plugins = self.cogs


    async def register_plugin(self, plugin):
        await super().add_cog(plugin)


    async def load_plugin(self, plugin):
        try:
            await super().load_extension(f"backend.plugins.{plugin}")
        except Exception:
            log.error(f"❌ Failed to load {plugin} - {traceback.format_exc()}")
        else:
            log.info(f"🔥 Successfully loaded {plugin}")

    
    async def reload_plugin(self, plugin):
        if plugin == "mod":
            in_plugins_name = "ModerationPlugin"
        elif plugin == "rr":
            in_plugins_name = "ReactionRolesPlugin"
        else:
            in_plugins_name = f"{plugin.capitalize()}Plugin"
        if in_plugins_name not in self.plugins:
            try: await super().load_extension(f"backend.plugins.{plugin}")
            except Exception: raise

        else:
            try: await super().unload_extension(f"backend.plugins.{plugin}")
            except Exception: raise

            else:
                try: await super().load_extension(f"backend.plugins.{plugin}")
                except Exception: raise


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
            log.warn(f"⚠️ Error while trying to mute user ({user.id}) (guild: {guild.id}) - {ex}"); exc = ex
        finally:
            return exc


    def get_uptime(self):
        raw = datetime.datetime.utcnow() - self.uptime

        hours, remainder = divmod(int(raw.total_seconds()), 3600)
        days, hours = divmod(hours, 24)
        minutes, seconds = divmod(remainder, 60)

        return "{}d, {}h, {}m & {}s".format(days, hours, minutes, seconds)


    def run(self):
        try:
            super().run(self.config.token, reconnect=True)
        finally:
            pass