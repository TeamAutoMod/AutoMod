import asyncio
import datetime
import aiohttp
from collections import deque, defaultdict

import discord
from discord import Intents
from discord.ext.commands import AutoShardedBot

from Bot import Handlers
from Utils import Utils
from Database import Connector, DBUtils


db = Connector.Database()


def prefix_callable(bot, message):
    prefixes = [f"<@!{bot.user.id}> ", f"<@{bot.user.id}> "]
    if message.guild is None:
        prefixes.append("+")
    elif bot.READY:
        try:
            prefix = DBUtils.get(db.configs, "guildId", f"{message.guild.id}", "prefix")
            if prefix is not None:
                prefixes.append(prefix)
            else:
                prefixes.append("+")
        except Exception:
            prefixes.append("+")
    return prefixes

class AutoMod(AutoShardedBot):
    READY = False
    version = ""
    command_count = 0
    custom_command_count = 0
    locked = True
    shard_count = 1
    shard_ids = []
    missing_guilds = []
    loading_task = None
    initial_fill_complete = False
    errors = 0
    own_messages = 0
    bot_messages = 0
    user_messages = 0
    cleans_running = dict()
    running_unbans = set()
    running_msg_deletions = set()
    running_removals = set()
    last_reload = None
    
    
    def __init__(self, shards=1):
        intents = Intents(
            guilds=True,
            members=True,
            bans=True,
            emojis=True,
            messages=True,
            reactions=True
        )
        super().__init__(
            command_prefix=prefix_callable, intents=intents, description="Discord moderation bot",
            case_insensitive=True, max_messages=1000, chunk_guilds_at_startup=False, shard_count=shards
        )
        self.total_shards = shards

        self.prev_events = deque(maxlen=10)

        self.resumes = defaultdict(list)
        self.identifies = defaultdict(list)


    def _clear_gateway_data(self):
        ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        for sid, dates in self.identifies.items():
            needs_removal = [i for i, dt in enumerate(dates) if dt < ago]
            for i in reversed(needs_removal):
                del dates[i]


        for sid, dates in self.resumes.items():
            needs_removal = [i for i, dt in enumerate(dates) if dt < ago]
            for i in reversed(needs_removal):
                del dates[i]


    async def _run_event(self, coro, event_name, *args, **kwargs):
        while (self.locked or not self.READY) and event_name != "on_ready":
            await asyncio.sleep(0.2)
        await super()._run_event(coro, event_name, *args, **kwargs)


    async def on_socket_response(self, message):
        self.prev_events.append(message)


    async def on_shard_resumed(self, sid):
        self.resumes[sid].append(datetime.datetime.utcnow())
        await Handlers.on_shard_resumed(self, sid)
    

    async def before_identify_hook(self, sid, *, initial):
        self._clear_gateway_data()
        self.identifies[sid].append(datetime.datetime.utcnow())
        await super().before_identify_hook(sid, initial=initial)


    async def on_ready(self):
        await Handlers.on_ready(self)


    async def on_message(self, message):
        await Handlers.on_message(self, message)


    async def on_guild_join(self, guild):
        await Handlers.on_guild_join(self, guild)


    async def on_guild_remove(self, guild):
        await Handlers.on_guild_remove(self, guild)


    async def on_command_error(self, ctx, error):
        await Handlers.on_command_error(self, ctx, error)


    async def on_guild_update(self, before, after):
        await Handlers.on_guild_update(before, after)


    def run(self):
        try:
            super().run(Utils.from_config("TOKEN"), reconnect=True)
        finally:
            with open("prev_events.log", "w", encoding="utf-8") as f:
                for data in self.prev_events:
                    try:
                        x = json.dumps(data, ensure_ascii=True, indent=4)
                    except:
                        f.write(f"{data}\n")
                    else:
                        f.write(f"{x}\n")