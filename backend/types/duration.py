import discord
from discord.ext import commands
from discord.ext.commands import BadArgument

import re



class DurationHolder(object):
    def __init__(self, length, unit=None) -> None:
        super().__init__()
        self.length = length
        self.unit = unit


    def to_seconds(self, ctx):
        if self.unit is None:
            self.unit = "seconds"
        unit = self.unit.lower()
        length = self.length
        if len(unit) > 1 and unit[-1:] == 's':
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
            raise BadArgument(ctx.bot.locale.t(ctx.guild, "invalid_lenth_unit"))
        max_length = 60 * 60 * 24 * 365
        if length > max_length:
            raise BadArgument(ctx.bot.locale.t(ctx.guild, "max_length", max_length=max_length))
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
        if argument.lower() not in \
            [
                "week", "weeks", "day", "days", "hour", "hours", "minute", 
                "minutes", "second","seconds", "w", "d", "h", "m", "s"
            ]:
            raise BadArgument(ctx.bot.locale.t(ctx.guild, "advanced_invalid_length_unit"))
        return argument



class Duration(commands.Converter):
    async def convert(self, ctx, argument):
        match = re.compile(r"^(\d+)").match(argument)
        if match is None:
            raise BadArgument("Duration is not a number")
        group = match.group(1)
        holder = DurationHolder(int(group))
        if len(argument) > len(group):
            holder.unit = await DurationIdentifier().convert(ctx, argument[len(group):])
        return holder