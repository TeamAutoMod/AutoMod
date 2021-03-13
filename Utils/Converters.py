import discord
from discord import NotFound, Forbidden, HTTPException
from discord.ext.commands import UserConverter, BadArgument, Converter

from i18n import Translator
from Utils.Matchers import ID_MATCHER, START_WITH_INT_RE, JUMP_LINK_RE
from Utils import Utils
from Bot.Handlers import PostParseError



class DiscordUser(Converter):
    def __init__(self, id_only=False) -> None:
        super().__init__()
        self.id_only = id_only

    async def convert(self, ctx, argument):
        user = None
        match = ID_MATCHER.match(argument)
        if match is not None:
            argument = match.group(1)
        try:
            user = await UserConverter().convert(ctx, argument)
        except BadArgument:
            try:
                user = await Utils.get_user(
                    await RangedInt(min=20000000000000000, max=9223372036854775807).convert(ctx, argument))
            except (ValueError, HTTPException):
                pass

        if user is None or (self.id_only and str(user.id) != argument):
            raise BadArgument("user_not_found")
        return user



class RangedInt(Converter):
    def __init__(self, min=None, max=None) -> None:
        self.min = min
        self.max = max

    async def convert(self, ctx, argument) -> int:
        try:
            argument = int(argument)
        except ValueError:
            raise BadArgument("NaN")
        else:
            if self.min is not None and argument < self.min:
                raise BadArgument("Number too small")
            elif self.max is not None and argument > self.max:
                raise BadArgument("Number too big")
            else:
                return argument


class UserID(Converter):
    def __init__(self):
        super().__init__()
    
    async def convert(self, ctx, argument):
        return (await DiscordUser().convert(ctx, argument)).id



class Guild(Converter):
    async def convert(self, ctx, argument):
        try:
            argument = int(argument)
        except ValueError:
            raise BadArgument("no_server_id")
        else:
            guild = ctx.bot.get_guild(argument)
            if guild is None:
                raise BadArgument("unkown_server")
            else:
                return guild


class DurationHolder:

    def __init__(self, dur, unit=None):
        super().__init__()
        self.dur = dur
        self.unit = unit

    def to_seconds(self, ctx):
        if self.unit is None:
            self.unit = "seconds"
        unit = self.unit.lower()
        dur = self.dur
        if len(unit) > 1 and unit[-1:] == 's':
            unit = unit[:-1]
        if unit == 'w' or unit == 'week':
            dur = dur * 7
            unit = 'd'
        if unit == 'd' or unit == 'day':
            dur = dur * 24
            unit = 'h'
        if unit == 'h' or unit == 'hour':
            dur = dur * 60
            unit = 'm'
        if unit == 'm' or unit == 'minute':
            dur = dur * 60
            unit = 's'
        if unit != 's' and unit != 'second':
            raise PostParseError('length', Translator.translate(ctx.guild, "invalid_lenth_unit"))
        max_dur = 60 * 60 * 24 * 365
        if dur > max_dur:
            raise PostParseError('length', Translator.translate(ctx.guild, "mex_lenth", max_length=max_langth))
        else:
            return dur

    def __str__(self):
        if len(self.unit) == 1:
            return f"{self.dur}{self.unit}"
        if self.unit[-1] != "s":
            return f"{self.dur} {self.unit}s"
        return f"{self.dur} {self.unit}"



class DurationIdentifier(Converter):
    async def convert(self, ctx, argument):
        if argument is None:
            argument = "seconds"
        if argument.lower() not in ["week", "weeks", "day", "days", "hour", "hours", "minute", "minutes", "second",
                                    "seconds", "w", "d", "h", "m", "s"]:
            raise BadArgument(Translator.translate(ctx.guild, "advanced_invalid_length_unit"))
        return argument



class Duration(Converter):
    async def convert(self, ctx, argument):
        match = START_WITH_INT_RE.match(argument)
        if match is None:
            raise BadArgument("NaN")
        group = match.group(1)
        holder = DurationHolder(int(group))
        if len(argument) > len(group):
            holder.unit = await DurationIdentifier().convert(ctx, argument[len(group):])
        return holder
    
