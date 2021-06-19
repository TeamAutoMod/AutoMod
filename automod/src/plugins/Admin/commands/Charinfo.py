import unicodedata


def toStr(char):
    digit = f"{ord(char):x}"
    name = unicodedata.name(char, "Name not found")
    return f"`\\U{digit:>08}`: {name} - {char} \N{EM DASH} <https://fileformat.info/info/unicode/char/{digit}>"


async def run(plugin, ctx, chars):
    msg = "\n".join(map(toStr, chars))
    await ctx.ensure_sending(msg)
