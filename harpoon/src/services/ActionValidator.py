import discord

import datetime
import traceback

from ..utils import Permissions



class ActionValidator:
    def __init__(self, bot):
        self.bot = bot
        self.punishments = {
            "warn": self.warn,
            "kick": self.kick,
            "ban": self.ban,
            "delete": self.delete
        }
        self.mute_length = {
            60: {
                "length": 1,
                "unit": "minute"
            },
            600: {
                "length": 10,
                "unit": "minutes"
            },
            1800: {
                "length": 30,
                "unit": "minutes"
            },
            3000: {
                "length": 1,
                "unit": "hour"
            }
        }   

    
    async def figure_it_out(self, message, guild, target, action, **kwargs):
        all_punishments = self.bot.db.configs.get(guild.id, "actions")
        _punishment = all_punishments[action]

        if len(_punishment.split("_")) > 1:
            if self.bot.db.configs.get(guild.id, "mute_role") == "":
                return
            
            mute_role = await self.bot.utils.getRole(guild, self.bot.db.configs.get(guild.id, "mute_role"))
            if mute_role is None:
                return

            try:
                await target.add_roles(mute_role)
            except Exception:
                if not mute_role in target.roles:
                    return
            
            punishment = _punishment.split("_")[0]
            length = int(_punishment.split("_")[-1])
            until = (datetime.datetime.utcnow() - datetime.timedelta(seconds=length))

            if self.bot.db.mutes.exists(f"{guild.id}-{target.id}"):
                return
            self.bot.db.mutes.insert(self.bot.schemas.Mute(guild.id, target.id, until))

            case = self.bot.utils.newCase(guild, "Mute", target, kwargs.get("moderator"), kwargs.get("reason"))
            new_kwargs = {
                "user": target,
                "user_id": target.id,
                "moderator": kwargs.get("moderator"),
                "moderator_id": kwargs.get("moderator_id"),
                "length": self.mute_length[length]["length"],
                "unit": self.mute_length[length]["unit"],
                "reason": kwargs.get("reason"),
                "case": case,
            }
            await self.bot.action_logger.log(guild, punishment, **new_kwargs)
        else:
            if Permissions.is_allowed(message, kwargs.get("moderator"), target):
                func = self.punishments[_punishment]
                await func(message, guild, target, **kwargs)
            else:
                return



    async def ban(self, message, guild, target, **kwargs):
        try:
            await guild.ban(user=target)
        except Exception:
            await self.delete(message, guild, target, **kwargs)
            return
        else:
            case = self.bot.utils.newCase(guild, "Ban", target, kwargs.get("moderator"), kwargs.get("reason"))
            new_kwargs = {
                "user": target,
                "user_id": target.id,
                "moderator": kwargs.get("moderator"), 
                "moderator_id": kwargs.get("moderator_id"), 
                "reason": kwargs.get("reason"),
                "case": case
            }
            await self.bot.action_logger.log(guild, "ban", **new_kwargs)


    async def kick(self, message, guild, target, **kwargs):
        try:
            await guild.kick(user=target)
        except Exception:
            await self.delete(message, guild, target, **kwargs)
            return
        else:
            case = self.bot.utils.newCase(guild, "Kick", target, kwargs.get("moderator"), kwargs.get("reason"))
            new_kwargs = {
                "user": target,
                "user_id": target.id,
                "moderator": kwargs.get("moderator"), 
                "moderator_id": kwargs.get("moderator_id"), 
                "reason": kwargs.get("reason"), 
                "case": case
            }
            await self.bot.action_logger.log(guild, "kick", **new_kwargs)


    async def warn(self, message, guild, target, **kwargs):
        new_kwargs = {
            "user": target,
            "user_id": target.id,
            "moderator": kwargs.get("moderator"), 
            "moderator_id": kwargs.get("moderator_id"), 
            "reason": kwargs.get("reason")
        }

        warn_id = f"{guild.id}-{target.id}"
        warns = self.bot.db.warns.get(warn_id, "warns")

        if warns == None:
            new_kwargs.update({
                "case": self.bot.utils.newCase(guild, "Warn", target, kwargs.get("moderator"), kwargs.get("reason"))
            })
            self.bot.db.warns.insert(self.bot.schemas.Warn(warn_id, 1))
            await self.bot.action_logger.log(guild, "warn", **new_kwargs)
        elif (warns+1) >= self.bot.db.configs.get(guild.id, "warn_threshold"):
            self.bot.db.warns.update(warn_id, "warns", 0)
            reason = kwargs.get("reason")
            kwargs.update({
                "reason": f"Automatic punishment escalation (Max warns) \n \n{reason}"
            })
            await self.figure_it_out(message, guild, target, "max_warns", **kwargs)
        else:
            new_kwargs.update({
                "case": self.bot.utils.newCase(guild, "Warn", target, kwargs.get("moderator"), kwargs.get("reason"))
            })
            self.bot.db.warns.update(warn_id, "warns", (warns+1))
            await self.bot.action_logger.log(guild, "warn", **new_kwargs)


    async def delete(self, message, guild, target, **kwargs):
        try:
            await message.delete()
        except Exception:
            pass
        _type = kwargs.get("_type")
        new_kwargs = {
            "user": target,
            "user_id": target.id,
            "moderator": kwargs.get("moderator"), 
            "moderator_id": kwargs.get("moderator_id"), 
            "reason": kwargs.get("reason"),
            "channel": message.channel.mention,
            "words": kwargs.get("words"),
            "unallowed": kwargs.get("unallowed"),
            "link": kwargs.get("link"),
            "position": kwargs.get("position"),
            "content": message.content
        }
        await self.bot.action_logger.log(guild, _type, **new_kwargs)
