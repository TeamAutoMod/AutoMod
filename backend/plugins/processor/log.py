import discord

from toolbox import S as Object
from typing import Union
import asyncio
import traceback
import logging; log = logging.getLogger(__name__)

from ...types import Embed
from ...bot import ShardedBotInstance


LOG_TYPES = {
    "ban": {
        "channel": "mod_log",
        "key": "log_ban",
        "color": 0xff5c5c,
        "emote": "HAMMER",
        "action": "User banned"
    },
    "kick": {
        "channel": "mod_log",
        "key": "log_kick",
        "color": 0xf79554,
        "emote": "SHOE",
        "action": "User kicked"
    },
    "hackban": {
        "channel": "mod_log",
        "key": "log_ban",
        "color": 0xff5c5c,
        "emote": "HAMMER",
        "action": "User forcebanned"
    },
    "softban": {
        "channel": "mod_log",
        "key": "log_ban",
        "color": 0xf79554,
        "emote": "HAMMER",
        "action": "User softbanned"
    },
    "tempban": {
        "channel": "mod_log",
        "key": "log_tempban",
        "color": 0xff5c5c,
        "emote": "HAMMER",
        "action": "User tempbanned"
    },
    "tempban_extended": {
        "channel": "mod_log",
        "key": "log_tempban_extended",
        "color": 0xff5c5c,
        "emote": "HAMMER",
        "action": "Tempban extended"
    },
    "unban": {
        "channel": "mod_log",
        "key": "log_unban",
        "color": 0x5cff9d,
        "emote": "UNLOCK",
        "action": "User unbanned"
    },
    "manual_unban": {
        "channel": "mod_log",
        "key": "log_manual_unban",
        "color": 0x5cff9d,
        "emote": "UNLOCK",
        "action": "User manually unbanned"
    },

    "mute": {
        "channel": "mod_log",
        "key": "log_mute",
        "color": 0xffdc5c,
        "emote": "MUTE",
        "action": "User muted"
    },
    "mute_extended": {
        "channel": "mod_log",
        "key": "log_mute_extended",
        "color": 0xffdc5c,
        "emote": "MUTE",
        "action": "Mute extended"
    },
    "unmute": {
        "channel": "mod_log",
        "key": "log_unmute",
        "color": 0x5cff9d,
        "emote": "UNMUTE",
        "action": "User unmuted"
    },
    "tempunban": {
        "channel": "mod_log",
        "key": "log_tempunban",
        "color": 0x5cff9d,
        "emote": "UNLOCK",
        "action": "User unbanned"
    },

    "warn": {
        "channel": "mod_log",
        "key": "log_warn",
        "color": 0xffdc5c,
        "emote": "FLAG",
        "action": "User warned"
    },
    "unwarn": {
        "channel": "mod_log",
        "key": "log_unwarn",
        "color": 0x5cff9d,
        "emote": "WHITE_FLAG",
        "action": "User unwarned"
    },
    "manual_unmute": {
        "channel": "mod_log",
        "key": "log_manual_unmute",
        "color": 0x5cff9d,
        "emote": "UNMUTE",
        "action": "User manually unmuted"
    },

    "message_deleted": {
        "channel": "message_log",
    },
    "message_edited": {
        "channel": "message_log",
    },

    "user_joined": {
        "channel": "join_log",
    },
    "user_left": {
        "channel": "join_log",
    },

    "role_created": {
        "channel": "server_log",
    },
    "role_deleted": {
        "channel": "server_log",
    },
    "role_updated": {
        "channel": "server_log",
    },

    "channel_created": {
        "channel": "server_log",
    },
    "channel_deleted": {
        "channel": "server_log",
    },
    "channel_updated": {
        "channel": "server_log",
    },

    "thread_created": {
        "channel": "server_log",
    },
    "thread_deleted": {
        "channel": "server_log",
    },
    "thread_updated": {
        "channel": "server_log",
    },

    "emoji_created": {
        "channel": "server_log",
    },
    "emoji_deleted": {
        "channel": "server_log",
    },

    "sticker_created": {
        "channel": "server_log",
    },
    "sticker_deleted": {
        "channel": "server_log",
    },

    "member_updated": {
        "channel": "member_log",
    },

    "joined_voice": {
        "channel": "voice_log",
    },
    "left_voice": {
        "channel": "voice_log",
    },
    "switched_voice": {
        "channel": "voice_log",
    },

    "automod_rule_triggered": {
        "channel": "mod_log",
        "key": "log_automod",
        "color": 0x2b80b8,
        "emote": "SWORDS",
        "action": "Automod rule triggered"
    },
    "regex_triggered": {
        "channel": "mod_log",
        "key": "log_regex",
        "color": 0x2b80b8,
        "emote": "NO_ENTRY",
        "action": "Regex filter triggered"
    },
    "filter_triggered": {
        "channel": "mod_log",
        "key": "log_filter",
        "color": 0x2b80b8,
        "emote": "NO_ENTRY",
        "action": "Word filter triggered"
    }
}


class LogProcessor(object):
    def __init__(self, bot: ShardedBotInstance) -> None:
        self.bot = bot
        self.db = bot.db
        self.queue = {}
        self.bot.loop.create_task(self.send_logs())


    async def send_logs(self):
        while True:
            await asyncio.sleep(2.5)
            for g, opt in self.queue.items():
                if sum([len(x) for x in opt.values()]) > 0:
                    for channel_type, entries in opt.items():
                        if len(entries) > 0:
                            chunk = entries[:max(min(3, len(entries)), 0)]
                            guild = self.bot.get_guild(g)

                            self.queue[g][channel_type] = [x for x in entries if x not in chunk]
                            if guild == None: return

                            log_channel_id = self.db.configs.get(guild.id, channel_type)
                            if log_channel_id == None or log_channel_id == "": return

                            log_channel: discord.TextChannel = guild.get_channel(int(log_channel_id))
                            if log_channel == None: return

                            await self._execute(
                                guild,
                                channel_type,
                                log_channel,
                                chunk
                            )


    async def default_log(self, channel: discord.TextChannel, chunk: list) -> dict:
        msgs = {}
        for entry in chunk:
            for e, has_case in entry.items():
                msg = await channel.send(embed=e)
                if has_case != False:
                    msgs.update(
                        {
                            has_case: msg
                        }
                    )
        return msgs


    async def fetch_webhook(self, wid: int) -> Union[discord.Webhook, None]:
        try:
            w = await self.bot.fetch_webhook(wid)
        except Exception:
            return None
        else:
            return w


    async def get_webhook(self, guild: discord.Guild, wid: int, channel_type: str) -> Union[discord.Webhook, None]:
        if not guild.id in self.bot.webhook_cache:
            w = await self.fetch_webhook(wid)
            if w == None: 
                return None
            else:
                self.bot.webhook_cache.update({
                    guild.id: {
                        **{
                            k: None for k in ["mod_log", "server_log", "message_log", "join_log", "member_log", "voice_log"] if k != channel_type
                        }, 
                        **{
                            channel_type: w
                        }
                    }
                })
                return w
        else:
            if self.bot.webhook_cache[guild.id][channel_type] == None:
                w = await self.fetch_webhook(wid)
                if w == None: 
                    return None
                else:
                    self.bot.webhook_cache[guild.id][channel_type] = w
                    return w
            else:
                if self.bot.webhook_cache[guild.id][channel_type] != wid:
                    w = await self.fetch_webhook(wid)
                    if w == None: 
                        return None
                    else:
                        self.bot.webhook_cache[guild.id][channel_type] = w
                        return w
                else:
                    return w


    async def execute(self, guild: discord.Guild, log_type: str, **log_kwargs) -> None:
        if not guild.id in self.queue: 
            self.queue[guild.id] = {
                "mod_log": [],
                "message_log": [],
                "server_log": [],
                "join_log": [],
                "member_log": [],
                "voice_log": []
            }

        config = Object(LOG_TYPES[log_type])
        if log_kwargs.get("_embed") == None:
            log_embed = Embed(
                color=config.color
            )
            log_embed.description = "{} **{}{}:** {} ({}) \n\n{}".format(
                self.bot.emotes.get(config.emote),
                f"#{log_kwargs.get('case')} " if "case" in log_kwargs else "",
                config.action,
                f"<@{log_kwargs.get('user_id')}>",
                log_kwargs.get("user_id"),
                self.bot.locale.t(guild, config.key, _emote=config.emote, **log_kwargs)
            )
        else:
            log_embed = log_kwargs.get("_embed")

        self.queue[guild.id][config.channel].append(
            {
                "embed": log_embed,
                "has_case": log_kwargs.get("case", False)
            }
        )

        log.info(self.queue)
        
        
    async def _execute(self, guild: discord.Guild, channel_type: str, log_channel: discord.TextChannel, chunk: dict) -> None:
        log_messages = {}
        try:
            wid = self.bot.db.configs.get(guild.id, f"{channel_type}_webhook")
            if wid != "":
                webhook = await self.get_webhook(
                    guild,
                    int(wid),
                    channel_type
                )
                if webhook == None:
                    log_messages = await self.default_log(log_channel, chunk)
                else:
                    try:
                        with_case = {x["embed"]: x["has_case"] for x in chunk if x["has_case"] != False}
                        without_case = [x["embed"] for x in chunk if x["has_case"] == False]

                        if len(with_case) > 0:
                            log_message = await webhook.send(embeds=list(with_case.keys()), wait=True)

                            for case in with_case.values():
                                log_messages.update(
                                    {
                                        case: log_message
                                    }
                                )

                        if len(without_case) > 0:
                            await webhook.send(embeds=without_case, wait=True)
                    except Exception:
                        log_messages = await self.default_log(log_channel, chunk)
            else:
                log_messages = await self.default_log(log_channel, chunk)
        
        except Exception:
            ex = traceback.format_exc()
            log.info(ex)
            pass
        else:
            if len(log_messages) > 0:
                for case, msg in log_messages.items():
                    self.db.cases.multi_update(f"{guild.id}-{case}", {
                        "log_id": f"{msg.id}",
                        "jump_url": f"{msg.jump_url}"
                    })