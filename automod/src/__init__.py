import discord
from discord.ext import commands

import logging
import asyncio
import time
import datetime
import traceback
import sys
from toolbox import S
from functools import wraps

from .i18n.Translator import Translator
from .services.Database import MongoDB, MongoSchemas
from .services.Caching import Cache
from .services.ActionLogger import ActionLogger
from .services.IgnoreForEvent import IgnoreForEvent
from .services.ActionValidator import ActionValidator
from .data.Emotes import Emotes
from .utils.ModifyConfig import ModifyConfig
from .utils.Context import Context
from .utils.BotUtils import BotUtils
from .plugins import PluginLoader
from .plugins.Types import Embed
from .utils.SlashCommand import SlashCommand



log = logging.getLogger(__name__)


def _prefix_callable(bot, message):
    base = [f"<@!{bot.user.id}> ", f"<@{bot.user.id}> "]
    if message.guild is None:
        base.append(bot.config.default_prefix)
    elif not bot.locked:
        try:
            prefix = bot.db.configs.get(message.guild.id, "prefix")
            base.append(prefix)
        except Exception:
            base.append(bot.config.default_prefix)
    return base


class AutoMod(commands.AutoShardedBot):
    def __init__(self, config: dict):
        self.config = config = S(config)
        # self.slash_commands = dict()
        intents = discord.Intents(
            guilds=True,
            members=True,
            bans=True,
            emojis=True,
            messages=True,
            reactions=True,
            voice_states=True
        )
        super().__init__(
           command_prefix=_prefix_callable, intents=intents, case_insensitive=True, 
           max_messages=1000, chunk_guilds_at_startup=True, shard_count=config.shards,
           allowed_mentions=discord.AllowedMentions(everyone=False)
        )
        self.ready = False
        self.locked = True

        self.used_commands = 0
        self.used_tags = 0
        self.total_shards = config.shards
        self.version = None

        self.i18next = Translator(self, config.langs)
        self.db = MongoDB(host=config.mongo_url).database
        self.schemas = MongoSchemas(self)
        self.cache = Cache(self)
        self.emotes = Emotes(self)
        self.action_logger = ActionLogger(self)
        self.ignore_for_event = IgnoreForEvent(self)
        self.action_validator = ActionValidator(self)
        self.utils = BotUtils(self)
        self.modify_config = ModifyConfig(self)


    # TODO slash commands...
    # def slash_command(self, description, perms):
    #     def decorator(func, description=description):
    #         name = func.__name__

    #         @wraps(func)
    #         def wrapper(*args, **kwargs):
    #             return func(*args, **kwargs)


    #         command = SlashCommand(
    #             name,
    #             description,
    #             perms,
    #             wrapper
    #         )

    #         self.slash_commands.update({
    #             name: command
    #         })

    #         return func
    #     return decorator

    
    async def on_ready(self):
        if not self.ready:
            if not self.config.dev:
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="loading..."), status=discord.Status.dnd)
            log.info("Starting up as {}#{} ({})".format(self.user.name, self.user.discriminator, self.user.id))
            self.fetch_guilds()

            for g in self.guilds:
                if g.id in self.config.blocked_guilds:
                    await g.leave()
                    log.info("Left blocked guild {}".format(g.id))

            self.uncached_guilds = {g.id: g for g in self.guilds}
            self.version = await self.utils.getVersion()
            
            try:
                for signal, signame in ("SIGTERM", "SIGINT"):
                    asyncio.get_event_loop().add_signal_handler(getattr(signal, signame), lambda: asyncio.ensure_future(self.logout()))
            except Exception:
                pass

            await self.chunk_guilds()

            log.info("Loading plugins...")
            await PluginLoader.loadPlugins(self)
            print(self.slash_commands)

            if not hasattr(self, "uptime"):
                self.uptime = datetime.datetime.utcnow()
            
            log.info("Ready!")

    
    async def chunk_guilds(self):
        start = time.time()

        for g in [x for x in self.guilds if isinstance(x, discord.Guild)]:
            if not self.db.configs.exists(f"{g.id}"):
                self.db.configs.insert(self.schemas.GuildConfig(g))
                log.info("Filled up missing guild {}".format(g.id))
        
        self.cache.build()

        end2 = time.time()
        final_dur = (end2 - start)
        log.info("Finished building internal cache in {}m".format(round(final_dur / 60, 1)))

        self.ready = True
        self.locked = False
        # if not self.config.dev:
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"commands | {self.config.default_prefix}help"), status=discord.Status.online)


    async def on_message(self, message):
        if message.guild is not None and self.ready:
            if not message.guild.chunked:
                await message.guild.chunk(cache=True)
                log.info("Cached missing guild {}".format(message.guild.id))

        ctx = await self.get_context(message, cls=Context) # TODO: fix this
        if ctx.valid and ctx.command is not None:
            self.used_commands = self.used_commands + 1
            if isinstance(ctx.channel, discord.DMChannel) or ctx.guild is None:
                return
            elif isinstance(ctx.channel, discord.TextChannel) and not ctx.channel.permissions_for(ctx.channel.guild.me).send_messages:
                try:
                    await ctx.author.send(self.i18next.t(ctx.guild, "cant_send_message"))
                except Exception:
                    pass
            else:
                await self.invoke(ctx)

    
    async def on_error(self, event, *args, **kwargs):
        error = sys.exc_info()
        e = Embed(
            color=0xff5c5c,
            title="Event Error",
            description="```py\n{}\n```".format("".join(
                traceback.format_exception(
                    etype=error[0], 
                    value=error[1], 
                    tb=error[2]
                )
            ))
        )
        e.add_field(
            name="❯ Event",
            value=f"{event}",
            inline=True
        )
        guild = args[0].guild or args[0]
        e.add_field(
            name="❯ Location",
            value="• Name: {} \n• ID: {}".format(
                guild.name or "None",
                guild.id or "None"
            ),
            inline=True
        )
        await self.utils.sendErrorLog(e)

    
    def get_uptime(self, display_raw=False):
        raw = datetime.datetime.utcnow() - self.uptime
        hours, remainder = divmod(int(raw.total_seconds()), 3600)
        days, hours = divmod(hours, 24)
        minutes, seconds = divmod(remainder, 60)
        if display_raw:
            return days, hours, minutes, seconds
        else:
            return "{}d, {}h, {}m & {}s".format(days, hours, minutes, seconds)


    def get_shard_ping(self, guild, ndigits=2):
        ping = round([x for i, x in self.shards.items() if i == guild.shard_id][0].latency * 1000, ndigits)
        return ping


    def get_guild_prefix(self, guild):
        prefix = self.db.configs.get(guild.id, "prefix")
        return prefix


    def run(self):
        try:
            super().run(self.config.token, reconnect=True)
        finally:
            pass