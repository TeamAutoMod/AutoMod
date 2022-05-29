import discord

from toolbox import S as Object
import logging; log = logging.getLogger(__name__)

from ...types import Embed



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
        "emote": "MORE",
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
        "color": 0xe67e22,
        "emote": "MUTE",
        "action": "User muted"
    },
    "mute_extended": {
        "channel": "mod_log",
        "key": "log_mute_extended",
        "color": 0xe67e22,
        "emote": "MORE",
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

    "used_command": {
        "channel": "bot_log"
    },
    "used_custom_command": {
        "channel": "bot_log"
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
    def __init__(
        self, 
        bot
    ) -> None:
        self.bot = bot
        self.db = bot.db


    async def execute(
        self, 
        guild: discord.Guild, 
        log_type: str, 
        **log_kwargs
    ) -> None:
        if not guild.id in self.bot.log_queue: 
            self.bot.log_queue[guild.id] = {
                "mod_log": [],
                "message_log": [],
                "server_log": [],
                "join_log": [],
                "member_log": [],
                "voice_log": [],
                "bot_log": []
            }

        config = Object(LOG_TYPES[log_type])
        if log_kwargs.get("_embed") == None:
            log_embed = Embed(
                None,
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
            fields = log_kwargs.get("extra_fields", [])
            if len(fields) > 0: log_embed.add_fields(fields)
        else:
            log_embed = log_kwargs.get("_embed")

        self.bot.log_queue[guild.id][config.channel].append(
            {
                "embed": log_embed,
                "has_case": log_kwargs.get("case", False)
            }
        )