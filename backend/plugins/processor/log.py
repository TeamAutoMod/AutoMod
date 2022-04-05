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
        "emote": "ANGEL",
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

    "emoji_created": {
        "channel": "server_log",
    },
    "emoji_deleted": {
        "channel": "server_log",
    },

    "automod_rule_triggered": {
        "channel": "mod_log",
        "key": "log_automod",
        "color": 0xff7514,
        "emote": "SHIELD",
        "action": "Automod rule triggered"
    },
    "regex_triggered": {
        "channel": "mod_log",
        "key": "log_regex",
        "color": 0xff7514,
        "emote": "SHIELD",
        "action": "Regex filter triggered"
    }
}


class LogProcessor(object):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db


    async def fetch_webhook(self, wid):
        try:
            w = await self.bot.fetch_webhook(wid)
        except Exception:
            return None
        else:
            return w


    async def get_webhook(self, bot, guild, wid, channel_type):
        if not guild.id in bot.webhook_cache:
            w = await self.fetch_webhook(wid)
            if w == None: 
                return None
            else:
                bot.webhook_cache.update({
                    guild.id: {
                        **{
                            k: None for k in ["mod_log", "server_log", "message_log", "join_log"] if k != channel_type
                        }, 
                        **{
                            channel_type: w
                        }
                    }
                })
                return w
        else:
            if bot.webhook_cache[guild.id][channel_type] == None:
                w = await self.fetch_webhook(wid)
                if w == None: 
                    return None
                else:
                    bot.webhook_cache[guild.id][channel_type] = w
                    return w
            else:
                if bot.webhook_cache[guild.id][channel_type] != wid:
                    w = await self.fetch_webhook(wid)
                    if w == None: 
                        return None
                    else:
                        bot.webhook_cache[guild.id][channel_type] = w
                        return w
                else:
                    return w



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
                f"<@{log_kwargs.get('user_id')}>",
                log_kwargs.get("user_id"),
                self.bot.locale.t(guild, config.key, _emote=config.emote, **log_kwargs)
            )
        else:
            log_embed = log_kwargs.get("_embed")


        try:
            wid = self.bot.db.configs.get(guild.id, f"{config.channel}_webhook")
            if wid != "":
                webhook = await self.get_webhook(
                    self.bot,
                    guild,
                    int(wid),
                    config.channel
                )
                if webhook == None:
                    log_message = await log_channel.send(content=log_kwargs.get("content", None), embed=log_embed)
                else:
                    try:
                        log_message = await webhook.send(content=log_kwargs.get("content", None), embed=log_embed, wait=True)
                    except Exception:
                        log_message = await log_channel.send(content=log_kwargs.get("content", None), embed=log_embed)
            else:
                log_message = await log_channel.send(content=log_kwargs.get("content", None), embed=log_embed)
        except Exception:
            pass
        else:
            if "case" in log_kwargs:
                self.db.cases.multi_update(f"{guild.id}-{log_kwargs.get('case')}", {
                    "log_id": f"{log_message.id}",
                    "jump_url": f"{log_message.jump_url}"
                })
