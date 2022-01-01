import discord
from discord.ext import tasks

from collections import OrderedDict
import datetime

from ...schemas import Warn, Case, Mute
from .modlog import ModlogProcessor



class ActionProcessor(object):
    def __init__(self, bot):
        self.bot = bot
        self.warns = self.bot.db.warns
        self.executors = {
            "kick": self.kick,
            "ban": self.ban,
            "mute": self.mute
        }
        self.modlog_processor = ModlogProcessor(bot)


    def new_case(self, _type, msg, mod, user, reason):
        case = self.bot.db.configs.get(msg.guild.id, "cases") + 1

        self.bot.db.inf.insert(Case(case, _type, msg, mod, user, reason))
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


    async def execute(self, msg, mod, user, warns, reason):
        log_kwargs = {
            "mod": f"{mod.name}#{mod.discriminator}",
            "mod_id": mod.id,
            "user": f"{user.name}#{user.discriminator}",
            "user_id": user.id,
            "reason": reason
        }
        warn_id = f"{msg.guild.id}-{user.id}"

        if mod.id == self.bot.user.id: 
            log_kwargs.update(
                {
                    "reason": f"[ Automatic ] {reason}"
                }
            )

        old_warns = 0
        new_warns = 0
        if not self.warns.exists(warn_id):
            self.warns.insert(Warn(warn_id))
        else:
            old_warns = self.warns.get(warn_id, "warns")
            new_warns = old_warns + warns; self.warns.update(warn_id, "warns", new_warns)

        rules = OrderedDict(sorted({int(x): y for x, y in self.bot.db.configs.get(msg.guild.id, "punishments").items() if int(x) <= new_warns}.items()))
        if len(rules) > 100:
            action = list(rules.values())[-1]
            _from = list(rules.keys())[-2] if len(list(rules.keys())) > 1 else 0
            _to = list(rules.keys())[-1]
            log_kwargs.update(
                {
                    "reason": f"[ Automatic {_to} ] {reason}",
                    "old_warns": _from,
                    "new_warns": _to
                }
            )

            if len(action.split(" ")) != 1:
                action = "mute"
                log_kwargs.update(
                    {
                        "length": int(action.split(" ")[1])
                    }
                )

            func = self.executors[action]
            return await func(msg, mod, user, reason, **log_kwargs)
        else:
            log_kwargs.update(
                {
                    "case": self.new_case("warn", msg, mod, user, reason),
                    "old_warns": old_warns,
                    "new_warns": new_warns
                }
            )
            await self.modlog_processor.execute(msg.guild, "warn", **log_kwargs)
            return None


    async def ban(self, msg, mod, user, reason, **log_kwargs):
        try:
            await msg.guild.ban(user=user)
        except Exception as ex:
            return ex
        else:
            log_kwargs.update(
                {
                    "case": self.new_case("ban", msg, mod, user, reason)
                }
            )
            await self.modlog_processor.execute(msg.guild, "ban", **log_kwargs)
            return None


    async def kick(self, msg, mod, user, reason, **log_kwargs):
        try:
            await msg.guild.kick(user=user)
        except Exception as ex:
            return ex
        else:
            log_kwargs.update(
                {
                    "case": self.new_case("kick", msg, mod, user, reason)
                }
            )
            await self.modlog_processor.execute(msg.guild, "ban", **log_kwargs)
            return None


    async def mute(self, msg, mod, user, reason, **log_kwargs):
        user = msg.guild.get_member(user.id);
        if user == None: return "User not found"

        if (msg.guild.me.guild_permissions.value & 0x10000000000) != 0x10000000000:
            if msg.guild.me.guild_permissions.administrator == False: 
                return "Missing permissions. Make sure I have the ``Timeout members`` permission"
        
        length = log_kwargs["length"]
        until = (datetime.datetime.utcnow() + datetime.timedelta(seconds=length))

        if self.bot.db.mutes.exists(f"{msg.guild.id}-{user.id}"): return
        self.bot.db.mutes.insert(Mute(msg.guild.id, msg.id, until))

        self.bot.handle_timeout(True, msg.guild, user, until.isoformat())

        log_kwargs.pop("length")
        log_kwargs.update(
            {
                "case": self.new_case("mute", msg, mod, user, reason),
                "until": f"<t:{round(until.timestamp())}:D>"
            }
        )
        await self.modlog_processor.execute(msg.guild, "mute", **log_kwargs)
        return None