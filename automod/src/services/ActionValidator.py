import datetime
import math
import traceback
from collections import OrderedDict



class ActionValidator:
    def __init__(self, bot):
        self.bot = bot
        self.punishments = {
            "kick": self.kick,
            "ban": self.ban
        }


    async def figure_it_out(self, message, target, action, **kwargs):
        _all = self.bot.db.configs.get(message.guild.id, "automod")
        try:
            opt = _all[action]
        except KeyError:
            return
        if "warns" in opt:
            warns = opt["warns"]
        elif opt is "mention":
            warns = abs(int(opt["threshold"]) - int(kwargs.get("mentions")))
        else:
            warns = math.ceil((float)(len(message.content.split("\n")) - int(opt["threhsold"])) / int(opt["threshold"]))

        if int(warns) < 1:
            return
        else:
            await self.add_warns(message, target, warns, **kwargs)



    async def add_warns(self, message, target, warns, **kwargs):
        _id = f"{message.guild.id}-{target.id}"
        if not self.bot.db.warns.exists(_id):
            old_warns = 0
            new_warns = warns
        else:
            old_warns = self.bot.db.warns.get(_id, "warns")
            new_warns = old_warns + warns

        if not self.bot.db.warns.exists(_id):
            self.bot.db.warns.insert(self.bot.schemas.Warn(_id, new_warns))
        else:
            self.bot.db.warns.update(_id, "warns", new_warns)
        
        punishments = OrderedDict(sorted({int(x): y for x, y in self.bot.db.configs.get(message.guild.id, "punishments").items() if int(x) <= new_warns}.items()))
        if len(punishments) > 0:
            action = list(punishments.values())[-1]
            _from = list(punishments.keys())[-2] if len(list(punishments.keys())) > 1 else 0
            _to = list(punishments.keys())[-1]
            if len(action.split(" ")) == 1:
                kwargs.update({
                    "reason": f"Automatic punishment escalation (warn {_to}): {kwargs.get('reason')}", 
                    "old_warns": _from,
                    "new_warns": _to
                })
                func = self.punishments[action]
                dm, case = await func(message, message.guild, target, **kwargs)
                return dm, case
            else:
                # Mute
                if self.bot.db.configs.get(message.guild.id, "mute_role") == "":
                    return
                
                mute_role = await self.bot.utils.getRole(message.guild, self.bot.db.configs.get(message.guild.id, "mute_role"))
                if mute_role is None:
                    return

                try:
                    await target.add_roles(mute_role)
                except Exception:
                    if not mute_role in target.roles:
                        return

                length = int(action.split(" ")[1])
                until = (datetime.datetime.utcnow() + datetime.timedelta(seconds=length))

                if self.bot.db.mutes.exists(f"{message.guild.id}-{target.id}"):
                    return
                self.bot.db.mutes.insert(self.bot.schemas.Mute(message.guild.id, target.id, until))

                case = self.bot.utils.newCase(message.guild, "Mute", target, kwargs.get("moderator"), kwargs.get("reason"))

                try:
                    last = message
                except Exception:
                    last = None

                dm = await self.bot.utils.dmUser(message, "mute", target, _emote="MUTE", guild_name=message.guild.name, length=int(action.split(" ")[-2]), unit=action.split(" ")[-1], reason=f"Automatic punishment escalation (warn {_to}): {kwargs.get('reason')}")
                new_kwargs = {
                    "user": target,
                    "user_id": target.id,
                    "moderator": kwargs.get("moderator"),
                    "moderator_id": kwargs.get("moderator_id"),
                    "length": int(action.split(" ")[-2]),
                    "unit": action.split(" ")[-1],
                    "reason": f"Automatic punishment escalation (warn {_to}): {kwargs.get('reason')}",
                    "context": f"\n**Context: ** [Here!]({last.jump_url})" if last is not None else "",
                    "case": case,
                    "dm": dm
                }
                await self.bot.action_logger.log(message.guild, "mute", **new_kwargs)
                return dm, case
        else:
            case = self.bot.utils.newCase(message.guild, "Warn", target, kwargs.get("moderator"), kwargs.get("reason"))

            try:
                last = message
            except Exception:
                last = None

            dm = await self.bot.utils.dmUser(message, "warn", target, _emote="WARN", warns=warns, guild_name=message.guild.name, reason=kwargs.get("reason"))
            new_kwargs = {
                "user": target,
                "user_id": target.id,
                "moderator": kwargs.get("moderator"),
                "moderator_id": kwargs.get("moderator_id"),
                "reason": kwargs.get("reason"),
                "old_warns": old_warns,
                "new_warns": new_warns,
                "warns": warns,
                "context": f"\n**Context: ** [Here!]({last.jump_url})" if last is not None else "",
                "case": case,
                "dm": dm
            }
            await self.bot.action_logger.log(message.guild, "warns_added", **new_kwargs)
            return dm, case



    async def ban(self, message, guild, target, **kwargs):
        try:
            await guild.ban(user=target)
        except Exception:
            await self.delete(message, guild, target, **kwargs)
            return
        else:
            
            case = self.bot.utils.newCase(guild, "Ban", target, kwargs.get("moderator"), kwargs.get("reason"))
            dm = await self.bot.utils.dmUser(message, "ban", target, _emote="HAMMER", guild_name=message.guild.name, reason=kwargs.get("moderator"))
            new_kwargs = {
                "user": target,
                "user_id": target.id,
                "moderator": kwargs.get("moderator"), 
                "moderator_id": kwargs.get("moderator_id"), 
                "reason": kwargs.get("reason"),
                "case": case,
                "dm": dm
            }
            await self.bot.action_logger.log(guild, "ban", **new_kwargs)
            return dm, case



    async def kick(self, message, guild, target, **kwargs):
        try:
            await guild.kick(user=target)
        except Exception:
            await self.delete(message, guild, target, **kwargs)
            return
        else:
            case = self.bot.utils.newCase(guild, "Kick", target, kwargs.get("moderator"), kwargs.get("reason"))
            dm = await self.bot.utils.dmUser(message, "kick", target, _emote="SHOE", guild_name=message.guild.name, reason=kwargs.get("reason"))
            new_kwargs = {
                "user": target,
                "user_id": target.id,
                "moderator": kwargs.get("moderator"), 
                "moderator_id": kwargs.get("moderator_id"), 
                "reason": kwargs.get("reason"), 
                "case": case,
                "dm": dm
            }

            await self.bot.action_logger.log(guild, "kick", **new_kwargs)
            return dm, case