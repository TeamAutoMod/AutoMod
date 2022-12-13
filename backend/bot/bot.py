# type: ignore

import discord
from discord.ext import commands

import json
import traceback
import requests
import datetime
import asyncio
from typing import Union, Tuple, Optional, Dict, List
import random
import os
import logging; log = logging.getLogger()

from .__obj__ import TypeHintedToolboxObject as Object
from .cache import InternalCache
from .mongo import MongoDB
from .schemas import GuildConfig, Stats
from .utils import Translator, Emotes, LogQueue, MessageCache
from .types import embed, Context
from .views import pages
from .observer import Observer 



def prefix_callable(bot, msg: discord.Message) -> List[str]:
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
        typing=False,
        voice_states=True
    )
    if hasattr(intents, "message_content"):
        intents.message_content = True
        
    def __init__(self, *args, **kwargs) -> None:
        self._start_text()
        with open("backend/bot/config.json", "r", encoding="utf8", errors="ignore") as config_file:
            self.config: Object = Object(json.load(config_file))
            if self.config.twitch_app_id != "" and self.config.twitch_secret != "":
                self.ngrok_port = random.randint(1024, 65535)
                #self._set_ngrok_url()
        super().__init__(
            command_prefix=prefix_callable, 
            intents=self.intents, 
            case_insensitive=True, 
            max_messages=1000, 
            chunk_guilds_at_startup=False, 
            allowed_mentions=discord.AllowedMentions(
                everyone=False, 
                replied_user=False
            ),
            *args, 
            **kwargs
        )
        for f in [pages, embed]: f.inject_bot_obj(self)

        self.ready = False
        self.locked = False
        self.avatar_as_bytes = None
        self.error_log = None
        self.uptime = datetime.datetime.utcnow()
        self.last_reload = datetime.datetime.utcnow().timestamp()

        self.used_commands = 0
        self.used_customs = 0

        self.command_stats: Dict[str, int] = {}
        self.ignore_for_events: List[int] = []
        self.case_cmd_cache: Dict[str, Dict[str, Tuple[int, List[embed.Embed]]]] = {}
        self.webhook_cache: Dict[int, discord.Webhook] = {}
        self.fetched_user_cache: Dict[int, discord.User] = {}
        self.log_queue: Dict[int, Dict[str, List[Dict[str, Tuple[embed.Embed, bool]]]]] = {}
        self.auto_processing: List[str] = []
        self.event_stats: Dict[str, int] = {}
        self.internal_cmd_store: Dict[str, int] = {}

        if self.config.watch == True:
            self.observer = Observer(self)

        self.db = MongoDB(self)
        self.cache = InternalCache(self)
        self.emotes = Emotes(self)
        self.locale = Translator(self)
        self._log_queue = LogQueue(self)
        self.message_cache = MessageCache()


    def _start_text(self) -> None:
        log.critical("\33[1m\33[34m" + """
     _         _        __  __           _ 
    / \  _   _| |_ ___ |  \/  | ___   __| |
   / _ \| | | | __/ _ \| |\/| |/ _ \ / _` |
  / ___ \ |_| | || (_) | |  | | (_) | (_| |
 /_/   \_\__,_|\__\___/|_|  |_|\___/ \__,_|
                                                                                                                                                    
            """ + "\33[0m") # we use log.critical() here to have it being interpreted as a log message for linux pm2 logs


    async def _activity_handler(self) -> None:
        while True:
            await asyncio.sleep(120)
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.playing if self.config.status_type.lower() not in [
                        "playing", "listening", "watching", "competing"
                    ] else getattr(discord.ActivityType, self.config.status_type.lower()), 
                    name=str(self.config.custom_status).format(
                        user_count=len(self.users),
                        guild_count=len(self.guilds)
                    )
                )
            )


    async def on_shard_connect(self, shard_id: int) -> None:
        log.info("[Sharding] Shard has connected", extra={"loc": f"Shard {shard_id}"})


    async def on_shard_disconnect(self, shard_id: int) -> None:
        log.error("[Sharding] Shard has disconnected", extra={"loc": f"Shard {shard_id}"})


    async def on_shard_ready(self, shard_id: int) -> None:
        log.info("[Sharding] Shard is ready", extra={"loc": f"Shard {shard_id}"})


    async def on_shard_resumed(self, shard_id: int) -> None:
        log.info("[Sharding] Shard has resumed session", extra={"loc":  f"Shard {shard_id}"})


    async def on_ready(self) -> None:
        if self.config.custom_status != "":
            if self.activity == None:
                await self.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.playing if self.config.status_type.lower() not in [
                            "playing", "listening", "watching", "competing"
                        ] else getattr(discord.ActivityType, self.config.status_type.lower()), 
                        name=str(self.config.custom_status).format(
                            user_count=len(self.users),
                            guild_count=len(self.guilds)
                        )
                    )
                )

        if not self.ready:
            await self.load_plugins()
            for cmd in self.tree.walk_commands():
                if hasattr(cmd, "description"):
                    setattr(
                        cmd,
                        "description",
                        f"{cmd.description[2:]}."
                    )
            
            await self.register_user_info_ctx_menu()
            await self.register_report_ctx_menu()
            await self.register_infractions_ctx_menu()
            await self.tree.sync()

            self.loop.create_task(self._log_queue.send_logs())
            self.loop.create_task(self.post_stats())

            if self.config.watch == True:
                await self.observer.start()

            for g in self.guilds:
                if not self.db.configs.exists(g.id):
                    self.db.configs.insert(GuildConfig(g, self.config.default_prefix))
            
            m = self.guilds[0].me
            if m != None:
                if m.avatar != None:
                    try:
                        self.avatar_as_bytes = await m.avatar.read()
                    except discord.HTTPException:
                        self.avatar_as_bytes = None
            
            if "{user_count}" in self.config.custom_status or "{guild_count}" in self.config.custom_status:
                self.loop.create_task(self._activity_handler())
            self.ready = True

    
    async def on_message(self, msg: discord.Message) -> None:
        if msg.author.bot or msg.guild is None:
            return
        else:
            if msg.content.lower() == f"<@{self.user.id}>":
                try:
                    await msg.channel.send(self.locale.t(msg.guild, "server_prefix"))
                except Exception:
                    pass
            else:
                if msg.guild != None:
                    ctx = await self.get_context(msg, cls=Context)
                    if ctx.valid and ctx.command is not None:
                        self.used_commands += 1
                        
                        if self.ready:
                            if not msg.guild.chunked:
                                await self.chunk_guild(msg.guild)
                        
                            await self.invoke(ctx)


    async def on_interaction(self, i: discord.Interaction) -> None:
        if i.type == discord.InteractionType.application_command:
            self.used_commands += 1
            self.update_command_stats()


    def dispatch(self, event_name: str, *args: Optional[discord.Interaction], **kwargs) -> None:
        ev = event_name.lower()
        if not "socket" in ev:
            self.event_stats.update({
                ev: self.event_stats.get(ev, 0) + 1
            })
        
        if ev == "interaction":
            if args[0].guild != None:
                if not args[0].guild.chunked:
                    asyncio.run_coroutine_threadsafe(self.chunk_guild(args[0].guild), loop=self.loop)
                    
        try:
            super().dispatch(event_name, *args, **kwargs)
        except Exception as ex:
            log.error(f"[Events] Error in {event_name} - {ex}", extra={"loc": f"PID {os.getpid()}"})
            
    
    async def load_plugins(self) -> None:
        try:
            self.remove_command("help")
        except Exception:
            pass
        finally:
            for p in self.config.plugins: 
                await self.load_plugin(p)
            self.plugins = self.cogs

            for cmd in self.config.disabled_commands:
                try:
                    self.remove_command(cmd)
                except Exception:
                    pass
            
            for cmd in await self.tree.fetch_commands():
                self.internal_cmd_store.update({
                    cmd.name: cmd.id
                })


    async def register_plugin(self, plugin: commands.Cog) -> None:
        await super().add_cog(plugin)


    async def load_plugin(self, plugin: str) -> None:
        try:
            await super().load_extension(f"backend.bot.plugins.{plugin}.plugin")
        except Exception:
            log.error(f"[Plugins] Failed to load {plugin} - {traceback.format_exc()}", extra={"loc": f"PID {os.getpid()}"})
        else:
            log.info(f"[Plugins] Successfully loaded {plugin}", extra={"loc": f"PID {os.getpid()}"})

    
    async def reload_plugin(self, plugin: str) -> None:
        if plugin == "mod":
            in_plugins_name = "ModerationPlugin"
        elif plugin == "rr":
            in_plugins_name = "ReactionRolesPlugin"
        elif plugin == "reply":
            in_plugins_name = "AutoReplyPlugin"
        elif plugin == "automod":
            in_plugins_name = "AutomodPlugin"
        elif plugin == "responder":
            in_plugins_name = "AutoResponderPlugin"
        else:
            in_plugins_name = f"{plugin.capitalize()}Plugin"
        
        if in_plugins_name not in self.plugins:
            try: await super().load_extension(f"backend.bot.plugins.{plugin}.plugin")
            except Exception: raise

        else:
            try: await super().unload_extension(f"backend.bot.plugins.{plugin}.plugin")
            except Exception: raise

            else:
                try: await super().load_extension(f"backend.bot.plugins.{plugin}.plugin")
                except Exception: raise


    def get_plugin(self, name: str) -> Optional[commands.Cog]:
        try:
            return super().get_cog(name)
        except Exception:
            return None


    def handle_timeout(self, mute: bool, guild: discord.Guild, user: Union[discord.Member, discord.User], iso8601_ts: str) -> Union[str, Exception]:
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
            log.warn(f"[Commands] Error while trying to mute user ({user.id}) (guild: {guild.id}) - {ex}", extra={"loc": f"Shard {guild.shard_id}"}); exc = ex
        finally:
            return exc


    def get_uptime(self, split: bool = False) -> str:
        raw = datetime.datetime.utcnow() - self.uptime

        hours, remainder = divmod(int(raw.total_seconds()), 3600)
        days, hours = divmod(hours, 24)
        minutes, seconds = divmod(remainder, 60)

        if split == False:
            return "{}d, {}h & {}m".format(days, hours, minutes)
        else:
            return days, hours, minutes, seconds
        

    def get_raw_uptime(self) -> datetime.timedelta:
        return datetime.datetime.utcnow() - self.uptime


    async def register_user_info_ctx_menu(self) -> None:
        @self.tree.context_menu(name="Userinfo")
        @discord.app_commands.default_permissions(manage_messages=True)
        async def _(i: discord.Interaction, user: discord.Member) -> None:
            p = self.get_plugin("UtilityPlugin")
            try:
                await p.whois._callback(p, i, user)
            except Exception as ex:
                await i.response.send_message(
                    embed=discord.Embed(
                        color=int(self.config.bot_color, 16),
                        description=self.locale.t(i.guild, "fail", _emote="NO", exc=ex)
                    )
                )
                

    async def register_report_ctx_menu(self) -> None:
        @self.tree.context_menu(name="Report")
        async def _(i: discord.Interaction, msg: discord.Message) -> None:
            p = self.get_plugin("ModerationPlugin")
            try:
                await p.report(i, msg)
            except Exception as ex:
                await i.response.send_message(
                    embed=discord.Embed(
                        color=int(self.config.embed_color, 16),
                        description=self.locale.t(i.guild, "fail", _emote="NO", exc=ex)
                    )
                )


    async def register_infractions_ctx_menu(self) -> None:
        @self.tree.context_menu(name="History")
        @discord.app_commands.default_permissions(manage_messages=True)
        async def _(i: discord.Interaction, user: discord.Member) -> None:
            p = self.get_plugin("CasesPlugin")
            try:
                await p.infractions._callback(p, i, str(user.id))
            except Exception as ex:
                await i.response.send_message(
                    embed=discord.Embed(
                        color=int(self.config.bot_color, 16),
                        description=self.locale.t(i.guild, "fail", _emote="NO", exc=ex)
                    )
                )


    def _post_stats(self) -> int:
        try:
            if self.config.web_url_base != "":
                r = requests.post(
                    f"{self.config.web_url_base}/pstats",
                    json={
                        "guilds": len(self.guilds),
                        "users": sum([x.member_count for x in self.guilds]),
                        "shards": self.shard_count,
                        "used_commands": self.get_command_stats(),
                        "token": self.config.token
                    }
                )
            else:
                return 0
        except Exception:
            return 0
        else:
            return r.status_code


    async def post_stats(self) -> None:
        while True:
            rc = self._post_stats()
            if rc != 0:
                if rc != 200:
                    log.warn(f"[Events] Failed to post stats to website ({rc})", extra={"loc": f"PID {os.getpid()}"})
                else:
                    log.info("[Events] Posted stats to website", extra={"loc": f"PID {os.getpid()}"})
            
            await asyncio.sleep(3600) # once every hour


    async def chunk_guild(self, guild: discord.Guild) -> None:
        if not guild.chunked:
            try:
                await guild.chunk(cache=True)
            except Exception:
                self._post_stats()
    

    async def join_thread(self, thread: discord.Thread) -> None:
        try:
            await thread.add_user(self.user)
        except Exception:
            pass

    
    def extract_args(self, i: discord.Interaction, *args) -> tuple:
        return (
            i.data["components"][i.data["components"].index(
                [_ for _ in i.data["components"] if _["components"][0]["custom_id"] == x][0]
            )]["components"][0].get("value", None) for x in args
        )


    def get_default_reason(self, guild: discord.Guild) -> str:
        return self.db.configs.get(guild.id, "default_reason")
    

    def update_command_stats(self) -> None:
        cur = self.db.stats.get(self.user.id, "used_commands")
        if cur == None:
            self.db.stats.insert(Stats(self.user.id))
        else:
            self.db.stats.update(self.user.id, "used_commands", cur + 1)


    def get_command_stats(self) -> int:
        cur = self.db.stats.get(self.user.id, "used_commands")
        if cur == None:
            self.db.stats.insert(Stats(self.user.id))
            return 0
        else:
            return cur


    def run(self) -> None:
        super().run(self.config.token, log_handler=None)