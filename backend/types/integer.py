from discord.ext import commands



class IntegerConverter(commands.Converter):
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    async def convert(self, ctx, argument):
        try:
            argument = int(argument)
        except ValueError:
            raise commands.BadArgument("Not a number")
        else:
            if self.min is not None and argument < self.min:
                raise commands.BadArgument("Number too small")
            elif self.max is not None and argument > self.max:
                raise commands.BadArgument("Number too big")
            else:
                return argument