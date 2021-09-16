import discord
from discord import HTTPException
from discord.ext import commands
from discord.ext.commands import BadArgument, UserConverter

from utils.RegEx import getPattern



class Embed(discord.Embed):
    def __init__(self, color=0x5765f0, **kwargs):
        super().__init__(color=color, **kwargs)
    

    def add_field(self, name, value, inline=False):
        super().add_field(name=name, value=value, inline=inline)
    

    def set_thumbnail(self, *args, **kwargs):
        super().set_thumbnail(*args, **kwargs)


    def set_footer(self, *args, **kwargs):
        super().set_footer(*args, **kwargs)



class DiscordUser(commands.Converter):
    def __init__(self, id_only=False) -> None:
        super().__init__()
        self.id_only = id_only

    async def convert(self, ctx, argument):
        user = None
        match = (getPattern(r"<@!?([0-9]+)>")).match(argument)
        if match is not None:
            argument = match.group(1)
        try:
            user = await UserConverter().convert(ctx, argument)
        except BadArgument:
            try:
                user = await ctx.bot.utils.getUser(
                    await RangedInt(min=20000000000000000, max=9223372036854775807).convert(ctx, argument))
            except (ValueError, HTTPException):
                pass

        if user is None or (self.id_only and str(user.id) != argument):
            raise BadArgument("user_not_found")
        return user



class RangedInt(commands.Converter):
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



class DiscordUserID(commands.Converter):
    def __init__(self):
        super().__init__()
    
    async def convert(self, ctx, argument):
        return (await DiscordUser().convert(ctx, argument)).id



class DurationHolder:

    def __init__(self, length, unit=None) -> None:
        super().__init__()
        self.length = length
        self.unit = unit

    def to_seconds(self, ctx):
        if self.unit is None:
            self.unit = "seconds"
        unit = self.unit.lower()
        length = self.length
        if len(unit) > 1 and unit[-1:] == 's':  # plural -> singular
            unit = unit[:-1]
        if unit == 'w' or unit == 'week':
            length = length * 7
            unit = 'd'
        if unit == 'd' or unit == 'day':
            length = length * 24
            unit = 'h'
        if unit == 'h' or unit == 'hour':
            length = length * 60
            unit = 'm'
        if unit == 'm' or unit == 'minute':
            length = length * 60
            unit = 's'
        if unit != 's' and unit != 'second':
            raise BadArgument(ctx.bot.i18next.translate(ctx.guild, "invalid_lenth_unit"))
        max_length = 60 * 60 * 24 * 365
        if length > max_length:
            raise BadArgument(ctx.bot.i18next.translate(ctx.guild, "max_length", max_length=max_length))
        else:
            return length

    def __str__(self):
        if len(self.unit) == 1:
            return f"{self.length}{self.unit}"
        if self.unit[-1] != "s":
            return f"{self.length} {self.unit}s"
        return f"{self.length} {self.unit}"



class DurationIdentifier(commands.Converter):
    async def convert(self, ctx, argument):
        if argument is None:
            argument = "seconds"
        if argument.lower() not in ["week", "weeks", "day", "days", "hour", "hours", "minute", "minutes", "second",
                                    "seconds", "w", "d", "h", "m", "s"]:
            raise BadArgument(ctx.bot.i18next.translate(ctx.guild, "advanced_invalid_length_unit"))
        return argument



class Duration(commands.Converter):
    async def convert(self, ctx, argument):
        match = getPattern(r"^(\d+)").match(argument)
        if match is None:
            raise BadArgument("NaN")
        group = match.group(1)
        holder = DurationHolder(int(group))
        if len(argument) > len(group):
            holder.unit = await DurationIdentifier().convert(ctx, argument[len(group):])
        return holder



class Reason(commands.Converter):
    async def convert(self, ctx, argument):
        if len(argument) > 200:
            return f"{argument[:197]}..."
        return argument
