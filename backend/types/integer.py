from discord.ext import commands

from typing import Union



class IntegerConverter(commands.Converter):
    def __init__(self, min: int = None, max: int = None) -> None:
        self.min = min
        self.max = max


    async def convert(self, ctx: commands.Context, argument: Union[int, str, None]) -> Union[int, Exception]:
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