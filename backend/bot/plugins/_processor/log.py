# type: ignore

import discord

from typing import Dict
from ...__obj__ import TypeHintedToolboxObject as Object
import logging; log = logging.getLogger(__name__)

from ...types import Embed



LOG_TYPES = {
    "ban": {
        "channel": "mod_log",
        "key": "log_ban",
        "color": 0xf04a47,
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
        "color": 0xf04a47,
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
        "color": 0xf04a47,
        "emote": "HAMMER",
        "action": "User tempbanned"
    },
    "tempban_extended": {
        "channel": "mod_log",
        "key": "log_tempban_extended",
        "color": 0xf04a47,
        "emote": "MORE",
        "action": "Tempban extended"
    },
    "unban": {
        "channel": "mod_log",
        "key": "log_unban",
        "color": 0x43b582,
        "emote": "UNLOCK",
        "action": "User unbanned"
    },
    "manual_unban": {
        "channel": "mod_log",
        "key": "log_manual_unban",
        "color": 0x43b582,
        "emote": "UNLOCK",
        "action": "User manually unbanned"
    },
    "manual_ban": {
        "channel": "mod_log",
        "key": "log_manual_ban",
        "color": 0xf04a47,
        "emote": "HAMMER",
        "action": "User manually banned"
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
        "color": 0x43b582,
        "emote": "UNMUTE",
        "action": "User unmuted"
    },
    "tempunban": {
        "channel": "mod_log",
        "key": "log_tempunban",
        "color": 0x43b582,
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
        "color": 0x43b582,
        "emote": "WHITE_FLAG",
        "action": "User unwarned"
    },
    "manual_unmute": {
        "channel": "mod_log",
        "key": "log_manual_unmute",
        "color": 0x43b582,
        "emote": "UNMUTE",
        "action": "User manually unmuted"
    },

    "automod": {
        "color": 0x2b80b8
    },
    "filter": {
        "color": 0x2b80b8
    },
    "regex": {
        "color": 0x2b80b8
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
    "bot_added": {
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
    },

    "report": {
        "channel": "report_log"
    }
}


class LogProcessor:
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = bot.db


    async def execute(self, guild: discord.Guild, log_type: str, **log_kwargs) -> None:
        if not guild.id in self.bot.log_queue: 
            self.bot.log_queue[guild.id] = {
                "mod_log": [],
                "message_log": [],
                "server_log": [],
                "join_log": [],
                "member_log": [],
                "voice_log": [],
                "report_log": []
            }

        config = Object(LOG_TYPES[log_type])
        if log_kwargs.get("_embed", None) == None:
            log_embed = Embed(
                None,
                color=config.color,
                description="{} **{}{}{}**".format(
                    self.bot.emotes.get(config.emote),
                    f"#{log_kwargs.get('case')} " if "case" in log_kwargs else "",
                    config.action,
                    f" ({log_kwargs.get('old_warns')} ➜ {log_kwargs.get('new_warns')})" if "old_warns" in log_kwargs else ""
                )
            )
            log_embed.add_fields([
                {
                    "name": "User",
                    "value": f"<@{log_kwargs.get('user_id')}> (``{log_kwargs.get('user_id')}``)",
                    "inline": True
                },
                log_embed.blank_field(inline=True),
                {
                    "name": "Moderator",
                    "value": f"<@{log_kwargs.get('mod_id')}> (``{log_kwargs.get('mod_id')}``)",
                    "inline": True
                }
            ])
            final_log_embed = self.resolve_kwargs(log_embed, **log_kwargs)

            fields = log_kwargs.get("extra_fields", [])
            if len(fields) > 0: final_log_embed.add_fields(fields)
        else:
            final_log_embed = log_kwargs.get("_embed")

        self.bot.log_queue[guild.id][config.channel].append(
            {
                "embed": final_log_embed,
                "has_case": log_kwargs.get("case", False)
            }
        )


    def resolve_kwargs(self, e: Embed, **kwargs) -> Embed:
        out = []
        for k, v in {
            x: y for x, y in kwargs.items() if y != None
        }.items():
            if k == "reason":
                out.append(self.create_field("Reason", f"{v}"))
            if k == "until":
                out.append(self.create_field("Expiration", f"{v}"))
            if k == "rule":
                out.append(self.create_field("Automod Rule", f"{v}"))
            elif k == "pattern" and v != "None":
                out.append(self.create_field("Filter/Regex", f"{v}"))
            if k == "found":
                out.append(self.create_field("Found Matches", f"{v}"))
            if k == "channel_id":
                out.append(self.create_field("Channel", f"<#{v}> (``{v}``)"))
            if k == "content":
                out.append(self.create_field("Message", f"```\n{v[:2000]}\n```"))

        e.add_fields(out)
        return e


    def create_field(self, name: str, value: str, inline: bool = False) -> Dict[str, str]:
        return {
            "name": name,
            "value": value,
            "inline": inline
        }
            