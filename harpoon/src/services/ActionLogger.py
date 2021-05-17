import datetime
import traceback



class ActionLogger:
    def __init__(self, bot):
        self.bot = bot
        self.t = bot.translator
        self.log_configs = {
            "ban": {
                "channel": "action_log_channel",
                "key": "log_ban",
                "on_time": True,
                "emote": "HAMMER"
            },
            "kick": {
                "channel": "action_log_channel",
                "key": "log_kick",
                "on_time": True,
                "emote": "SHOE"
            },
            "forceban": {
                "channel": "action_log_channel",
                "key": "log_forceban",
                "on_time": True,
                "emote": "HAMMER"
            },
            "softban": {
                "channel": "action_log_channel",
                "key": "log_softban",
                "on_time": True,
                "emote": "HAMMER"
            },
            "cleanban": {
                "channel": "action_log_channel",
                "key": "log_cleanban",
                "on_time": True,
                "emote": "HAMMER"
            },
            "unban": {
                "channel": "action_log_channel",
                "key": "log_unban",
                "on_time": True,
                "emote": "UNLOCK"
            },
            "manual_unban": {
                "channel": "action_log_channel",
                "key": "log_manual_unban",
                "on_time": True,
                "emote": "UNLOCK"
            },

            "mass_ban": {
                "channel": "action_log_channel",
                "key": "log_mass_ban",
                "on_time": True,
                "emote": "HAMMER2"
            },
            "mass_kick": {
                "channel": "action_log_channel",
                "key": "log_mass_kick",
                "on_time": True,
                "emote": "SHOE"
            },

            "mute": {
                "channel": "action_log_channel",
                "key": "log_mute",
                "on_time": True,
                "emote": "MUTE"
            },
            "mute_extended": {
                "channel": "action_log_channel",
                "key": "log_mute_extended",
                "on_time": True,
                "emote": "MUTE"
            },
            "unmute": {
                "channel": "action_log_channel",
                "key": "log_unmute",
                "on_time": True,
                "emote": "UNMUTE"
            },
            "manual_unmute": {
                "channel": "action_log_channel",
                "key": "log_manual_unmute",
                "on_time": True,
                "emote": "UNMUTE"
            },
            "reapplied_mute": {
                "channel": "action_log_channel",
                "key": "log_reapplied_mute",
                "on_time": True,
                "emote": "UNMUTE"
            },

            "warn": {
                "channel": "action_log_channel",
                "key": "log_warn",
                "on_time": True,
                "emote": "WARN"
            },
            "warn_clearing": {
                "channel": "action_log_channel",
                "key": "log_warn_clearing",
                "on_time": True,
                "emote": "UNLOCK"
            },
            "inf_claim": {
                "channel": "action_log_channel",
                "key": "log_inf_claim",
                "on_time": True,
                "emote": "EYES"
            },

            "censor": {
                "channel": "action_log_channel",
                "key": "log_censor",
                "on_time": True,
                "emote": "CENSOR"
            },
            "invite": {
                "channel": "action_log_channel",
                "key": "log_invite",
                "on_time": True,
                "emote": "CENSOR"
            },
            "zalgo": {
                "channel": "action_log_channel",
                "key": "log_zalgo",
                "on_time": True,
                "emote": "CENSOR"
            },
            "file": {
                "channel": "action_log_channel",
                "key": "log_file",
                "on_time": True,
                "emote": "CENSOR"
            },
            "mention": {
                "channel": "action_log_channel",
                "key": "log_mention",
                "on_time": True,
                "emote": "CENSOR"
            },
            "caps": {
                "channel": "action_log_channel",
                "key": "log_caps",
                "on_time": True,
                "emote": "CENSOR"
            },
            "spam_detected": {
                "channel": "action_log_channel",
                "key": "log_spam",
                "on_time": True,
                "emote": "SHOE"
            },

            "voice_join": {
                "channel": "voice_log_channel",
                "key": "voice_channel_join",
                "on_time": True,
                "emote": "BLUEDOT"
            },
            "voice_leave": {
                "channel": "voice_log_channel",
                "key": "voice_channel_leave",
                "on_time": True,
                "emote": "REDDOT"
            },
            "voice_switch": {
                "channel": "voice_log_channel",
                "key": "voice_channel_switch",
                "on_time": True,
                "emote": "SWITCH"
            },

            "message_deleted": {
                "channel": "message_log_channel",
                "key": "log_message_deletion",
                "on_time": True,
                "emote": "BIN"
            },
            "message_edited": {
                "channel": "message_log_channel",
                "key": "log_message_edit",
                "on_time": True,
                "emote": "PEN"
            },

            "member_join": {
                "channel": "join_log_channel",
                "key": "log_join",
                "on_time": True,
                "emote": "JOIN"
            },
            "member_leave": {
                "channel": "join_log_channel",
                "key": "log_leave",
                "on_time": True,
                "emote": "LEAVE"
            },
            "member_join_cases": {
                "channel": "join_log_channel",
                "key": "log_join_with_prior_cases",
                "on_time": True,
                "emote": "WARN"
            },

            "clean": {
                "channel": "action_log_channel",
                "key": "log_clean",
                "on_time": True,
                "emote": "CLEAN"
            }
        }


    async def log(self, guild, log_type, **kwargs):
        if not log_type in self.log_configs:
            raise Exception("Invalid log type")
        
        conf = self.log_configs[log_type]

        log_channel_id = self.bot.db.configs.get(guild.id, conf["channel"])
        if log_channel_id == None or log_channel_id == "":
            return
        
        log_channel = await self.bot.utils.getChannel(guild, log_channel_id)
        if log_channel is None:
            return

        log_key = conf["key"]
        log_emote = conf["emote"]
        if conf["on_time"]:
            kwargs.update({
                "on_time": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            })
        try:
            await log_channel.send(self.t.translate(guild, log_key, _emote=log_emote, **kwargs))
        except Exception:
            pass