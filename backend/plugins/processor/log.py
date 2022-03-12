from toolbox import S as Object

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
    "forceban": {
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

    "warn": {
        "channel": "mod_log",
        "key": "log_warn",
        "color": 0xffdc5c,
        "emote": "ALARM",
        "action": "User warned"
    },
    "unwarn": {
        "channel": "mod_log",
        "key": "log_unwarn",
        "color": 0x5cff9d,
        "emote": "UNLOCK",
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
        "key": "", # not needed
        "color": 0xff5c5c,
        "emote": "BIN",
        "action": "" # not needed
    },
    "message_edited": {
        "channel": "message_log",
        "key": "", # not needed
        "color": 0xffdc5c,
        "emote": "PEN", 
        "action": "" # not needed
    },

    "user_joined": {
        "channel": "server_log",
        "key": "", # not needed
        "color": 0x5cff9d,
        "emote": "JOIN"
    },
    "user_left": {
        "channel": "server_log",
        "key": "", # not needed
        "color": 0xff5c5c,
        "emote": "LEAVE"
    },
}


class LogProcessor(object):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db


    async def execute(self, guild, log_type, **log_kwargs):
        config = Object(LOG_TYPES[log_type])

        log_channel_id = self.db.configs.get(guild.id, config.channel)
        if log_channel_id == None or log_channel_id == "": return

        log_channel = guild.get_channel(int(log_channel_id))
        if log_channel == None: return

        if log_kwargs.get("_embed") == None:
            log_embed = Embed(
                color=config.color
            )
            log_embed.description = "{} **{}{}:** {} ({}) \n\n{}".format(
                self.bot.emotes.get(config.emote),
                f"#{log_kwargs.get('case')} " if "case" in log_kwargs else "",
                config.action,
                log_kwargs.get("user"),
                log_kwargs.get("user_id"),
                self.bot.locale.t(guild, config.key, _emote=config.emote, **log_kwargs)
            )
        else:
            log_embed = log_kwargs.get("_embed")
    
        try:
            log_message = await log_channel.send(content=log_kwargs.get("content", None), embed=log_embed)
        except Exception:
            pass
        else:
            if "case" in log_kwargs:
                self.db.cases.multi_update(f"{guild.id}-{log_kwargs.get('case')}", {
                    "log_id": f"{log_message.id}",
                    "jump_url": f"{log_message.jump_url}"
                })
