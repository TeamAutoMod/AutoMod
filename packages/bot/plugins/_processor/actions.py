import discord

from collections import OrderedDict
import datetime

from typing import Union

from ...bot import ShardedBotInstance
from ...schemas import Warn, Case, Mute, Tempban
from .log import LogProcessor
from .dm import DMProcessor



class ActionProcessor(object):
    def __init__(
        self, 
        bot: ShardedBotInstance
    ):
        self.bot = bot
        self.warns = self.bot.db.warns
        self.executors = {
            "kick": self.kick,
            "ban": self.ban,
            "mute": self.mute,
            "tempban": self.tempban
        }
        self.log_processor = LogProcessor(bot)
        self.dm_processor = DMProcessor(bot)


    def new_case(
        self, 
        _type: str, 
        msg: discord.Message, 
        mod: discord.Member, 
        user: Union[
            discord.Member, 
            discord.User
        ], 
        reason: str, 
        warns_added: int = 0, 
        until: datetime.datetime = None
    ) -> int:
        case = self.bot.db.configs.get(msg.guild.id, "cases") + 1

        if self.bot.db.cases.exists(f"{msg.guild.id}-{case}"):
            self.bot.db.cases.delete(f"{msg.guild.id}-{case}") # we need to overwrite old cases
        
        now = datetime.datetime.utcnow()
        self.bot.db.cases.insert(Case(case, _type, msg, mod, user, reason, now, warns_added, until))
        self.bot.db.configs.update(msg.guild.id, "cases", case)

        case_ids = self.bot.db.configs.get(msg.guild.id, "case_ids")
        case_ids.update(
            {
                f"{case}": {
                    "mod": f"{mod.id}",
                    "user": f"{user.id}",
                    "guild": f"{msg.guild.id}"
                }
            }
        )
        self.bot.db.configs.update(msg.guild.id, "case_ids", case_ids)
        return case


    async def execute(
        self, 
        msg: discord.Message, 
        mod: discord.Member, 
        user: Union[
            discord.Member, 
            discord.User
        ], 
        warns: int, 
        reason: str, 
        **special_log_kwargs
    ) -> None:
        if "(" in reason:
            raw_reason = reason.split("(")[0]
        else:
            raw_reason = reason

        log_kwargs = {
            "mod": mod,
            "mod_id": mod.id,
            "user": f"{user.name}#{user.discriminator}",
            "user_id": user.id,
            "reason": reason,
            "raw_reason": raw_reason,
            **special_log_kwargs
        }
        if not "channel_id" in log_kwargs:
            log_kwargs.update({
                "channel_id": msg.channel.id
            })

        warn_id = f"{msg.guild.id}-{user.id}"

        if mod.id == self.bot.user.id: 
            log_kwargs.update(
                {
                    "reason": f"{reason}, automated by AutoMod"
                }
            )

        old_warns = 0
        new_warns = 0
        if not self.warns.exists(warn_id):
            self.warns.insert(Warn(warn_id, warns)); new_warns = warns
        else:
            old_warns = self.warns.get(warn_id, "warns")
            new_warns = old_warns + warns; self.warns.update(warn_id, "warns", new_warns)

        rules = OrderedDict(
            sorted(
                {
                    int(x): y for x, y in self.bot.db.configs.get(msg.guild.id, "punishments").items() if int(x) <= new_warns
                }.items()
            )
        )
        if len(rules) <  100 and len(rules) > 0:
            action = list(rules.values())[-1]
            _from = list(rules.keys())[-2] if len(list(rules.keys())) > 1 else 0
            _to = list(rules.keys())[-1]
            reason = f"{reason} (Escalation {_to})"

            log_kwargs.update(
                {
                    "reason": reason,
                    "old_warns": _from,
                    "new_warns": _to
                }
            )

            if len(action.split(" ")) != 1:
                log_kwargs.update(
                    {
                        "length": int(action.split(" ")[1])
                    }
                )
                if action.split(" ")[0] == "mute":
                    action = "mute"
                else:
                    action = "tempban"

            func = self.executors[action]
            return await func(msg, mod, user, reason, **log_kwargs)
        else:
            self.dm_processor.execute(
                msg,
                "warn",
                user,
                **{
                    "guild_name": msg.guild.name,
                    "reason": raw_reason,
                    "_emote": "ALARM"
                }
            )

            log_kwargs.update(
                {
                    "case": self.new_case("warn", msg, mod, user, reason, warns_added=warns),
                    "old_warns": old_warns,
                    "new_warns": new_warns
                }
            )
            await self.log_processor.execute(msg.guild, "warn", **log_kwargs)
            return None


    async def ban(
        self, 
        msg: discord.Message, 
        _mod: discord.Member, 
        _user: Union[
            discord.Member, 
            discord.User
        ], 
        _reason: str, 
        **log_kwargs
    ) -> Union[
        None, 
        Exception
    ]:
        mod, user, reason = _mod, _user, _reason
        if msg.guild.get_member(user.id) == None: return "User not found"
        if f"{msg.guild.id}-{user.id}" in self.bot.auto_processing: return "Already banning user"

        self.bot.auto_processing.append(f"{msg.guild.id}-{user.id}")
        try:
            await msg.guild.ban(user=user)
        except Exception as ex:
            return ex
        else:
            self.bot.ignore_for_events.append(user.id)
            self.dm_processor.execute(
                msg,
                "ban",
                user,
                **{
                    "guild_name": msg.guild.name,
                    "reason": log_kwargs.get("raw_reason"),
                    "_emote": "HAMMER"
                }
            )

            log_kwargs.update(
                {
                    "case": self.new_case("ban", msg, mod, user, reason)
                }
            )
            await self.log_processor.execute(msg.guild, "ban", **log_kwargs)
            return None
        finally:
            self.bot.auto_processing.remove(f"{msg.guild.id}-{user.id}")


    async def kick(
        self, 
        msg: discord.Message, 
        _mod: discord.Member, 
        _user: Union[
            discord.Member, 
            discord.User
        ], 
        _reason: str, 
        **log_kwargs
    ) -> Union[
        None, 
        Exception
    ]:
        mod, user, reason = _mod, _user, _reason
        if msg.guild.get_member(user.id) == None: return "User not found"
        if f"{msg.guild.id}-{user.id}" in self.bot.auto_processing: return "Already kicking user"

        self.bot.auto_processing.append(f"{msg.guild.id}-{user.id}")
        try:
            await msg.guild.kick(user=user)
        except Exception as ex:
            return ex
        else:
            self.bot.ignore_for_events.append(user.id)
            self.dm_processor.execute(
                msg,
                "kick",
                user,
                **{
                    "guild_name": msg.guild.name,
                    "reason": log_kwargs.get("raw_reason"),
                    "_emote": "SHOE"
                }
            )

            log_kwargs.update(
                {
                    "case": self.new_case("kick", msg, mod, user, reason)
                }
            )
            await self.log_processor.execute(msg.guild, "kick", **log_kwargs)
            return None
        finally:
            self.bot.auto_processing.remove(f"{msg.guild.id}-{user.id}")


    async def mute(
        self, 
        msg: discord.Message, 
        _mod: discord.Member, 
        _user: Union[
            discord.Member, 
            discord.User
        ], 
        _reason: str, 
        **log_kwargs
    ) -> Union[
        None, 
        Exception
    ]:
        mod, user, reason = _mod, _user, _reason
        user = msg.guild.get_member(user.id)
        if user == None: return "User not found"

        if (msg.guild.me.guild_permissions.value & 0x10000000000) != 0x10000000000:
            if msg.guild.me.guild_permissions.administrator == False: 
                return "Missing permissions. Make sure I have the ``Timeout members`` permission"

        if f"{msg.guild.id}-{user.id}" in self.bot.auto_processing: return "Already kicking user"
        self.bot.auto_processing.append(f"{msg.guild.id}-{user.id}")

        try:
            length = log_kwargs["length"]
            until = (datetime.datetime.utcnow() + datetime.timedelta(seconds=length))

            if self.bot.db.mutes.exists(f"{msg.guild.id}-{user.id}"): return
            self.bot.db.mutes.insert(Mute(msg.guild.id, user.id, until))

            self.bot.handle_timeout(True, msg.guild, user, until.isoformat())

            self.dm_processor.execute(
                msg,
                "mute",
                user,
                **{
                    "guild_name": msg.guild.name,
                    "until": f"<t:{round(until.timestamp())}>",
                    "reason": log_kwargs.get("raw_reason"),
                    "_emote": "MUTE"
                }
            )

            log_kwargs.pop("length")
            log_kwargs.update(
                {
                    "case": self.new_case("mute", msg, mod, user, reason, until=until),
                    "until": f"<t:{round(until.timestamp())}>"
                }
            )
            await self.log_processor.execute(msg.guild, "mute", **log_kwargs)
            return None
        except Exception as ex:
            return ex
        finally:
            self.bot.auto_processing.remove(f"{msg.guild.id}-{user.id}")

    
    async def tempban(
        self, 
        msg: discord.Message, 
        _mod: discord.Member, 
        _user: Union[
            discord.Member, 
            discord.User
        ], 
        _reason: str, 
        **log_kwargs
    ) -> Union[
        None, 
        Exception
    ]:
        mod, user, reason = _mod, _user, _reason
        user = msg.guild.get_member(user.id);
        if user == None: return "User not found"
        
        if f"{msg.guild.id}-{user.id}" in self.bot.auto_processing: return "Already kicking user"
        self.bot.auto_processing.append(f"{msg.guild.id}-{user.id}")

        length = log_kwargs["length"]
        until = (datetime.datetime.utcnow() + datetime.timedelta(seconds=length))

        if self.bot.db.tbans.exists(f"{msg.guild.id}-{user.id}"): return
        self.bot.db.tbans.insert(Tempban(msg.guild.id, user.id, until))

        try:
            await msg.guild.ban(user=user)
        except Exception as ex:
            return ex
        else:
            self.bot.ignore_for_events.append(user.id)

            self.dm_processor.execute(
                msg,
                "tempban",
                user,
                **{
                    "guild_name": msg.guild.name,
                    "until": f"<t:{round(until.timestamp())}>",
                    "reason": log_kwargs.get("raw_reason"),
                    "_emote": "HAMMER"
                }
            )

            log_kwargs.pop("length")
            log_kwargs.update(
                {
                    "case": self.new_case("tempban", msg, mod, user, reason, until=until),
                    "until": f"<t:{round(until.timestamp())}>"
                }
            )
            await self.log_processor.execute(msg.guild, "tempban", **log_kwargs)
            return None
        finally:
            self.bot.auto_processing.remove(f"{msg.guild.id}-{user.id}")